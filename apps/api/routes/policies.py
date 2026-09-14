from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from ..state import app_state
from quoin.kernel.models import PolicyRecord, PolicyRule
from quoin.kernel.hasher import CanonicalHasher

router = APIRouter(prefix="/api/policies", tags=["Policies"])

class CutoverRequest(BaseModel):
    new_generation: Optional[int] = None
    max_gold_discount: float = 1000.0
    max_standard_discount: float = 500.0
    visibility_lag_seconds: float = 0.35

@router.get("")
def get_current_policy(tenant_id: str = "agency_operations"):
    snapshot = app_state.memory.get_active_snapshot(tenant_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="No active policy found for tenant")
    return {
        "status": "ACTIVE",
        "tenant_id": tenant_id,
        "generation": snapshot.generation,
        "policy_id": snapshot.policy_id,
        "policy_hash": snapshot.retrieved_record_hash,
        "visible_at": snapshot.visible_at.isoformat(),
        "rules": [r.model_dump() for r in (snapshot.policy_record.rules if snapshot.policy_record else [])]
    }

@router.post("/cutover")
def trigger_cutover(req: CutoverRequest, tenant_id: str = "agency_operations"):
    current = app_state.memory.get_active_snapshot(tenant_id)
    current_gen = current.generation if current else 17
    next_gen = req.new_generation or (current_gen + 1)

    now = datetime.now(timezone.utc)
    new_policy = PolicyRecord(
        policy_id=f"pol_agency_v{next_gen}",
        generation=next_gen,
        version_hash=f"v{next_gen}_cutover",
        effective_at=now,
        scope="commercial_operations",
        rules=[
            PolicyRule(rule_id=f"r_disc_std_g{next_gen}", client_tier="standard", max_discount_amount=req.max_standard_discount),
            PolicyRule(rule_id=f"r_disc_gold_g{next_gen}", client_tier="gold", max_discount_amount=req.max_gold_discount),
            PolicyRule(rule_id=f"r_credit_g{next_gen}", client_tier="standard", max_credit_amount=500.0),
        ]
    )

    ack, ack_ms = app_state.memory.ingest_policy(
        tenant_id=tenant_id,
        policy=new_policy,
        visibility_lag=req.visibility_lag_seconds
    )

    return {
        "status": "ACCEPTED",
        "message": f"Policy update to G{next_gen} submitted and accepted.",
        "previous_generation": current_gen,
        "new_generation": next_gen,
        "acknowledgement_latency_ms": round(ack_ms, 2),
        "visibility_lag_seconds": req.visibility_lag_seconds,
        "policy_hash": CanonicalHasher.compute_policy_hash(new_policy)
    }

@router.post("/force_sync")
def force_sync(tenant_id: str = "agency_operations"):
    app_state.memory.force_make_visible(tenant_id)
    snap = app_state.memory.get_active_snapshot(tenant_id)
    return {
        "status": "SYNCHRONIZED",
        "active_generation": snap.generation if snap else 0
    }

@router.post("/reset")
def reset_policy(tenant_id: str = "agency_operations"):
    app_state.memory.ingest_policy(tenant_id, app_state.policy_g17, visibility_lag=0.0)
    app_state.memory.force_make_visible(tenant_id)
    return {"status": "RESET", "active_generation": 17}
