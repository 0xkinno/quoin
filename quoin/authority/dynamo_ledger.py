"""Authoritative Policy Ledger & Two-Phase Commit Engine (Plane B / Channel B).

Provides durable, optimistic locking, conditional writes, and transactional
guarantees for authoritative policy epochs using Amazon DynamoDB or local durable fallback.
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from dotenv import dotenv_values
from ..kernel.models import PolicyRecord, PolicyRule
from ..kernel.hasher import CanonicalHasher
from ..config import get_config

class DynamoAuthorityLedger:
    """Authoritative Policy Store enforcing atomic cutovers and single-use permits."""

    def __init__(self, table_name: Optional[str] = None, region: Optional[str] = None):
        self.table_name = table_name or get_config("DYNAMODB_TABLE_NAME") or get_config("QUOIN_DYNAMODB_TABLE")
        self.region = region or get_config("AWS_REGION", "us-east-1")
        self.access_key = get_config("AWS_ACCESS_KEY_ID")
        self.secret_key = get_config("AWS_SECRET_ACCESS_KEY")

        self.db_path = Path(__file__).resolve().parent.parent.parent / "evidence" / "authority_ledger.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_sqlite()

        self._dynamo_client = None
        self.dynamodb_error: Optional[str] = None
        if self.table_name and self.access_key and self.secret_key:
            try:
                import boto3
                session = boto3.Session(
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region,
                )
                self._dynamo_client = session.resource("dynamodb")
            except Exception as e:
                self.dynamodb_error = str(e)
                print(f"[WARN] DynamoDB connection error: {e}. Using durable local ledger.")

    def _init_sqlite(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS policy_epochs (
                    tenant_id TEXT PRIMARY KEY,
                    policy_id TEXT NOT NULL,
                    epoch INTEGER NOT NULL,
                    policy_hash TEXT NOT NULL,
                    rules_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS consumed_permits (
                    permit_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    epoch INTEGER NOT NULL,
                    policy_hash TEXT NOT NULL,
                    effect_hash TEXT NOT NULL,
                    committed_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def get_authoritative_epoch(self, tenant_id: str) -> Tuple[int, str, Optional[PolicyRecord]]:
        """Retrieve current authoritative epoch, canonical hash, and policy record."""
        # 1. Try DynamoDB if configured
        if self._dynamo_client and self.table_name:
            try:
                table = self._dynamo_client.Table(self.table_name)
                res = table.get_item(Key={"tenant_id": tenant_id})
                item = res.get("Item")
                if item:
                    rules = [PolicyRule(**r) for r in json.loads(item["rules_json"])]
                    rec = PolicyRecord(
                        policy_id=item["policy_id"],
                        generation=int(item["epoch"]),
                        version_hash=item["policy_hash"],
                        effective_at=datetime.fromisoformat(item["updated_at"]),
                        scope="commercial",
                        rules=rules,
                    )
                    return int(item["epoch"]), item["policy_hash"], rec
            except Exception as e:
                self.dynamodb_error = str(e)
                print(f"[WARN] DynamoDB read error: {e}")

        # 2. Local Durable SQLite Store
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT policy_id, epoch, policy_hash, rules_json, updated_at FROM policy_epochs WHERE tenant_id = ?",
                (tenant_id,)
            )
            row = cursor.fetchone()
            if row:
                policy_id, epoch, policy_hash, policy_json, updated_at = row
                try:
                    data = json.loads(policy_json)
                    if isinstance(data, dict) and "rules" in data:
                        rec = PolicyRecord(**data)
                    else:
                        rules = [PolicyRule(**r) for r in data]
                        rec = PolicyRecord(
                            policy_id=policy_id,
                            generation=epoch,
                            version_hash=policy_hash,
                            effective_at=datetime.fromisoformat(updated_at),
                            scope="commercial",
                            rules=rules,
                        )
                except Exception:
                    rules = [PolicyRule(**r) for r in json.loads(policy_json)]
                    rec = PolicyRecord(
                        policy_id=policy_id,
                        generation=epoch,
                        version_hash=policy_hash,
                        effective_at=datetime.fromisoformat(updated_at),
                        scope="commercial",
                        rules=rules,
                    )
                return epoch, policy_hash, rec

        # Default genesis state (G17)
        genesis_rules = [
            PolicyRule(rule_id="r_std", client_tier="standard", max_discount_amount=500.0, max_discount_percentage=10.0),
            PolicyRule(rule_id="r_gold", client_tier="gold", max_discount_amount=1500.0, max_discount_percentage=20.0),
        ]
        genesis_rec = PolicyRecord(
            policy_id="pol_commercial_standard_v1",
            generation=17,
            version_hash="genesis_hash_v1",
            effective_at=datetime(2026, 9, 14, 0, 0, 0, tzinfo=timezone.utc),
            scope="commercial",
            rules=genesis_rules,
        )
        h = CanonicalHasher.hash_policy(genesis_rec)
        genesis_rec.version_hash = h
        self.set_initial_policy(tenant_id, genesis_rec, h)
        return 17, h, genesis_rec

    def set_initial_policy(self, tenant_id: str, policy: PolicyRecord, policy_hash: str):
        policy_json = json.dumps(policy.model_dump(), default=str)
        eff_iso = policy.effective_at.isoformat()
        if self._dynamo_client and self.table_name:
            try:
                table = self._dynamo_client.Table(self.table_name)
                table.put_item(
                    Item={
                        "tenant_id": tenant_id,
                        "policy_id": policy.policy_id,
                        "epoch": policy.generation,
                        "policy_hash": policy_hash,
                        "rules_json": policy_json,
                        "updated_at": eff_iso,
                    }
                )
            except Exception as e:
                self.dynamodb_error = str(e)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO policy_epochs (tenant_id, policy_id, epoch, policy_hash, rules_json, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (tenant_id, policy.policy_id, policy.generation, policy_hash, policy_json, eff_iso)
            )
            conn.commit()

    def conditional_cutover(
        self,
        tenant_id: str,
        expected_epoch: int,
        new_policy: PolicyRecord,
    ) -> Tuple[bool, int, str]:
        """Perform optimistic locking conditional cutover: epoch must equal expected_epoch."""
        new_hash = CanonicalHasher.hash_policy(new_policy)
        new_policy.version_hash = new_hash
        policy_json = json.dumps(new_policy.model_dump(), default=str)
        eff_iso = new_policy.effective_at.isoformat()

        # 1. DynamoDB conditional update
        if self._dynamo_client and self.table_name:
            try:
                table = self._dynamo_client.Table(self.table_name)
                table.put_item(
                    Item={
                        "tenant_id": tenant_id,
                        "policy_id": new_policy.policy_id,
                        "epoch": new_policy.generation,
                        "policy_hash": new_hash,
                        "rules_json": policy_json,
                        "updated_at": eff_iso,
                    },
                    ConditionExpression="epoch = :exp OR attribute_not_exists(epoch)",
                    ExpressionAttributeValues={":exp": expected_epoch},
                )
                # Succeeded in DynamoDB; keep SQLite mirror updated
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO policy_epochs (tenant_id, policy_id, epoch, policy_hash, rules_json, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (tenant_id, new_policy.policy_id, new_policy.generation, new_hash, policy_json, eff_iso)
                    )
                    conn.commit()
                return True, new_policy.generation, new_hash
            except Exception as e:
                err_code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
                if err_code == "ConditionalCheckFailedException" or "ConditionalCheckFailedException" in str(e):
                    return False, expected_epoch, f"CAS Epoch Mismatch in DynamoDB: {e}"
                # If DynamoDB is inaccessible or has permission issues, record error and fall back to SQLite
                self.dynamodb_error = str(e)

        # 2. SQLite atomic conditional update
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT epoch FROM policy_epochs WHERE tenant_id = ?", (tenant_id,))
            row = cursor.fetchone()
            current_epoch = row[0] if row else 0

            if current_epoch != expected_epoch:
                return False, current_epoch, f"CAS Epoch Mismatch: expected G{expected_epoch}, found G{current_epoch}"

            cursor.execute(
                """UPDATE policy_epochs 
                   SET epoch = ?, policy_hash = ?, rules_json = ?, updated_at = ? 
                   WHERE tenant_id = ? AND epoch = ?""",
                (new_policy.generation, new_hash, policy_json, eff_iso, tenant_id, expected_epoch)
            )
            if cursor.rowcount == 1:
                conn.commit()
                return True, new_policy.generation, new_hash
            else:
                return False, current_epoch, "Concurrent modification collision"

    def is_permit_consumed(self, permit_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM consumed_permits WHERE permit_id = ?", (permit_id,))
            return cursor.fetchone() is not None

    def consume_permit_atomic(
        self,
        permit_id: str,
        request_id: str,
        epoch: int,
        policy_hash: str,
        effect_hash: str,
    ) -> bool:
        """Single-use atomic permit consumption."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    """INSERT INTO consumed_permits 
                       (permit_id, request_id, epoch, policy_hash, effect_hash, committed_at) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (permit_id, request_id, epoch, policy_hash, effect_hash, now_iso)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def status(self) -> Dict[str, Any]:
        return {
            "table_name": self.table_name,
            "region": self.region,
            "dynamodb_configured": bool(self.table_name and self._dynamo_client),
            "dynamodb_error": self.dynamodb_error,
            "active_storage": "dynamodb" if (self._dynamo_client and not self.dynamodb_error) else "sqlite_durable_ledger",
        }
