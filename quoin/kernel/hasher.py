"""Canonical hashing and deterministic cryptographic digests for QUOIN."""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict
from pydantic import BaseModel

class CanonicalHasher:
    """Provides deterministic SHA-256 serialization and digest calculation."""

    @staticmethod
    def _to_canonical_dict(obj: Any) -> Any:
        if isinstance(obj, BaseModel):
            return CanonicalHasher._to_canonical_dict(obj.model_dump())
        elif isinstance(obj, dict):
            return {k: CanonicalHasher._to_canonical_dict(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return [CanonicalHasher._to_canonical_dict(item) for item in obj]
        elif isinstance(obj, datetime):
            # Ensure timezone-aware UTC ISO string
            if obj.tzinfo is None:
                obj = obj.replace(tzinfo=timezone.utc)
            else:
                obj = obj.astimezone(timezone.utc)
            return obj.isoformat()
        elif isinstance(obj, float):
            # Canonical float formatting
            return round(obj, 6)
        return obj

    @classmethod
    def serialize(cls, data: Any) -> bytes:
        canonical_obj = cls._to_canonical_dict(data)
        serialized = json.dumps(canonical_obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        return serialized.encode("utf-8")

    @classmethod
    def digest(cls, data: Any) -> str:
        return hashlib.sha256(cls.serialize(data)).hexdigest()

    @classmethod
    def compute_policy_hash(cls, policy_record: Any) -> str:
        if isinstance(policy_record, BaseModel):
            dumped = policy_record.model_dump(exclude={"version_hash"})
        elif isinstance(policy_record, dict):
            dumped = {k: v for k, v in policy_record.items() if k != "version_hash"}
        else:
            dumped = policy_record
        return cls.digest(dumped)

    @classmethod
    def compute_request_hash(cls, request_data: Dict[str, Any]) -> str:
        return cls.digest(request_data)

    @classmethod
    def compute_proposal_hash(cls, proposal: Any) -> str:
        return cls.digest(proposal)

    @classmethod
    def compute_effect_hash(cls, action: str, parameters: Dict[str, Any]) -> str:
        payload = {"action": action, "parameters": parameters}
        return cls.digest(payload)

    @classmethod
    def compute_receipt_id(cls, request_id: str, generation: int, effect_hash: str) -> str:
        raw = f"{request_id}:{generation}:{effect_hash[:16]}"
        return f"rcpt_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"

    @classmethod
    def compute_permit_id(cls, receipt_id: str, effect_hash: str) -> str:
        raw = f"{receipt_id}:{effect_hash}"
        return f"prmt_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"

    @classmethod
    def sign_permit(cls, permit_id: str, receipt_id: str, effect_hash: str, generation: int) -> str:
        payload = f"QUOIN_KERNEL_V1:{permit_id}:{receipt_id}:{effect_hash}:{generation}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
