"""Idempotency and replay prevention ledger for Plane D side effects."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ExecutionRecord(BaseModel):
    """Immutable audit record of a committed side effect."""
    permit_id: str
    receipt_id: str
    request_id: str
    effect_hash: str
    generation: int
    executed_at: datetime
    result: Dict[str, Any]
    replay_count: int = 0

class IdempotencyLedger:
    """In-memory or persistent store preventing duplicate effect executions."""

    def __init__(self):
        self._records_by_permit: Dict[str, ExecutionRecord] = {}
        self._records_by_fingerprint: Dict[str, ExecutionRecord] = {}

    def get_existing(self, permit_id: str, request_id: str, effect_hash: str) -> Optional[ExecutionRecord]:
        if permit_id in self._records_by_permit:
            rec = self._records_by_permit[permit_id]
            rec.replay_count += 1
            return rec
        
        fingerprint = f"{request_id}:{effect_hash}"
        if fingerprint in self._records_by_fingerprint:
            rec = self._records_by_fingerprint[fingerprint]
            rec.replay_count += 1
            return rec

        return None

    def record_execution(
        self,
        permit_id: str,
        receipt_id: str,
        request_id: str,
        generation: int,
        effect_hash: str,
        result: Dict[str, Any],
    ) -> ExecutionRecord:
        now = datetime.now(timezone.utc)
        record = ExecutionRecord(
            permit_id=permit_id,
            receipt_id=receipt_id,
            request_id=request_id,
            generation=generation,
            effect_hash=effect_hash,
            executed_at=now,
            result=result,
        )
        self._records_by_permit[permit_id] = record
        fingerprint = f"{request_id}:{effect_hash}"
        self._records_by_fingerprint[fingerprint] = record
        return record

    def count(self) -> int:
        return len(self._records_by_permit)
