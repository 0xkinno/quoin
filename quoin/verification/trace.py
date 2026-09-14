"""Decision Trace / Immutable Forensic Timeline (Plane B & Proof Plane).

Implements cryptographically chained forensic decision traces:
trace_hash_n = SHA256(trace_hash_(n-1) || canonical_json(event_n))
"""

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from ..kernel.hasher import CanonicalHasher

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

class DecisionTraceLedger:
    """Manages immutable, append-only, chained decision timelines."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (Path(__file__).resolve().parent.parent.parent / "evidence" / "decision_traces.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decision_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    sequence_index INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    current_hash TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    UNIQUE(request_id, sequence_index)
                )
            """)
            conn.commit()

    @staticmethod
    def compute_step_hash(previous_hash: str, event_data: Dict[str, Any]) -> str:
        canonical_bytes = CanonicalHasher.to_canonical_json(event_data).encode("utf-8")
        h = hashlib.sha256()
        h.update(previous_hash.encode("utf-8"))
        h.update(canonical_bytes)
        return h.hexdigest()

    def append_event(
        self,
        request_id: str,
        event_type: str,
        event_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Append a new forensic event to the request's decision trace."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT sequence_index, current_hash FROM decision_events WHERE request_id = ? ORDER BY sequence_index DESC LIMIT 1",
                (request_id,)
            )
            row = cursor.fetchone()
            if row:
                seq_idx = row[0] + 1
                prev_hash = row[1]
            else:
                seq_idx = 1
                prev_hash = GENESIS_HASH

            now_iso = datetime.now(timezone.utc).isoformat()
            canonical_payload_data = json.loads(json.dumps(CanonicalHasher._to_canonical_dict(event_data), default=str))
            payload = {
                "request_id": request_id,
                "sequence_index": seq_idx,
                "event_type": event_type,
                "payload": canonical_payload_data,
                "timestamp": now_iso,
            }
            curr_hash = self.compute_step_hash(prev_hash, payload)

            cursor.execute(
                """INSERT INTO decision_events 
                   (request_id, sequence_index, event_type, event_data_json, previous_hash, current_hash, timestamp) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (request_id, seq_idx, event_type, json.dumps(payload, default=str), prev_hash, curr_hash, now_iso)
            )
            conn.commit()

            return {
                "sequence_index": seq_idx,
                "event_type": event_type,
                "previous_hash": prev_hash,
                "current_hash": curr_hash,
                "timestamp": now_iso,
                "payload": event_data,
            }

    def get_trace(self, request_id: str) -> List[Dict[str, Any]]:
        """Retrieve the complete chronological event sequence for a request."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT sequence_index, event_type, event_data_json, previous_hash, current_hash, timestamp 
                   FROM decision_events WHERE request_id = ? ORDER BY sequence_index ASC""",
                (request_id,)
            )
            rows = cursor.fetchall()
            events = []
            for r in rows:
                data = json.loads(r[2])
                events.append({
                    "sequence_index": r[0],
                    "event_type": r[1],
                    "payload": data.get("payload", {}),
                    "previous_hash": r[3],
                    "current_hash": r[4],
                    "timestamp": r[5],
                })
            return events

    def verify_trace(self, request_id: str) -> Tuple[bool, str, Optional[int]]:
        """Cryptographically recomputes the entire chain from genesis to head."""
        events = self.get_trace(request_id)
        if not events:
            return False, "TRACE_NOT_FOUND", None

        expected_prev = GENESIS_HASH
        for ev in events:
            payload = {
                "request_id": request_id,
                "sequence_index": ev["sequence_index"],
                "event_type": ev["event_type"],
                "payload": ev["payload"],
                "timestamp": ev["timestamp"],
            }
            computed = self.compute_step_hash(expected_prev, payload)
            if computed != ev["current_hash"] or ev["previous_hash"] != expected_prev:
                return False, "TRACE_ALTERED", ev["sequence_index"]
            expected_prev = computed

        return True, "TRACE_INTACT", len(events)
