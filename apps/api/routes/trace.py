"""Decision Trace & Forensic Timeline API Router (Phase 4 & Proof Plane).

Exposes cryptographically chained event inspection and verification.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from quoin.verification.trace import DecisionTraceLedger, GENESIS_HASH
from quoin.kernel.hasher import CanonicalHasher

router = APIRouter(prefix="/api/trace", tags=["Decision Trace"])
trace_ledger = DecisionTraceLedger()

class VerifyTraceRequest(BaseModel):
    request_id: Optional[str] = None
    events: Optional[List[Dict[str, Any]]] = None

def seed_sample_trace_if_needed(request_id: str = "req_sample_fenced_01"):
    existing = trace_ledger.get_trace(request_id)
    if existing:
        return existing

    # Seed an authentic 5-step sample trace
    trace_ledger.append_event(
        request_id=request_id,
        event_type="REQUEST_INGESTED",
        event_data={
            "client_id": "cust_enterprise_42",
            "tier": "gold",
            "action": "apply_discount",
            "amount": 750.0,
            "invoice_id": "inv_9042",
            "claimed_generation": 18
        }
    )
    trace_ledger.append_event(
        request_id=request_id,
        event_type="REASONING_PROPOSAL_FORMULATED",
        event_data={
            "agent_plane": "Plane A (Strands / Bedrock)",
            "observed_policy_generation": 18,
            "rationale": "Evaluated $750.0 discount for gold tier under visible G18 limits ($1000.0).",
            "proposal_hash": "a4f89d32b170c29188e04b08170c2918"
        }
    )
    trace_ledger.append_event(
        request_id=request_id,
        event_type="GENERATION_FENCE_PERMITTED",
        event_data={
            "kernel_plane": "Plane B (Deterministic Kernel)",
            "verified_generation": 18,
            "policy_hash": "c89f01ab4321defa76543210fedcba98",
            "receipt_id": "rcpt_750_g18_gold",
            "status": "PERMITTED"
        }
    )
    trace_ledger.append_event(
        request_id=request_id,
        event_type="READ_AFTER_WRITE_CAS_VERIFIED",
        event_data={
            "gate_plane": "Plane B (Two-Phase Commit Gate)",
            "read_generation": 18,
            "expected_generation": 18,
            "cas_match": True,
            "permit_id": "prmt_750_g18_single_use"
        }
    )
    trace_ledger.append_event(
        request_id=request_id,
        event_type="IDEMPOTENT_EFFECT_COMMITTED",
        event_data={
            "execution_plane": "Plane D (Operational Action Service)",
            "action": "apply_discount",
            "discount_amount": 750.0,
            "replay_status": "FRESH_EXECUTION",
            "execution_id": "prmt_750_g18_single_use",
            "status": "SUCCESS"
        }
    )
    return trace_ledger.get_trace(request_id)

@router.get("/sample")
def get_sample_trace():
    """Retrieve an authentic pre-seeded sample decision trace."""
    events = seed_sample_trace_if_needed("req_sample_fenced_01")
    valid, status, count = trace_ledger.verify_trace("req_sample_fenced_01")
    return {
        "request_id": "req_sample_fenced_01",
        "events": events,
        "verification": {
            "valid": valid,
            "status": status,
            "step_count": count,
            "genesis_hash": GENESIS_HASH,
            "head_hash": events[-1]["current_hash"] if events else None,
        }
    }

@router.get("/{request_id}")
def get_trace(request_id: str):
    """Retrieve full chronological decision trace for a given request."""
    if request_id == "req_sample_fenced_01" or request_id == "sample":
        return get_sample_trace()

    events = trace_ledger.get_trace(request_id)
    if not events:
        raise HTTPException(status_code=404, detail=f"No decision trace found for request {request_id}")

    valid, status, count = trace_ledger.verify_trace(request_id)
    return {
        "request_id": request_id,
        "events": events,
        "verification": {
            "valid": valid,
            "status": status,
            "step_count": count,
            "head_hash": events[-1]["current_hash"] if events else None,
        }
    }

@router.post("/verify")
def verify_trace_endpoint(payload: VerifyTraceRequest):
    """Cryptographically recompute SHA-256 chain to detect any tampering."""
    if payload.request_id and not payload.events:
        valid, status, count = trace_ledger.verify_trace(payload.request_id)
        events = trace_ledger.get_trace(payload.request_id)
        return {
            "request_id": payload.request_id,
            "valid": valid,
            "status": "TRACE INTACT" if valid else "TRACE ALTERED",
            "verified_steps": count,
            "tampered_step": None if valid else count,
            "head_hash": events[-1]["current_hash"] if events else None,
        }

    if payload.events:
        events = payload.events
        expected_prev = GENESIS_HASH
        for i, ev in enumerate(events):
            req_id = ev.get("request_id") or (payload.request_id or "adhoc")
            p = {
                "request_id": req_id,
                "sequence_index": ev["sequence_index"],
                "event_type": ev["event_type"],
                "payload": ev.get("payload", {}),
                "timestamp": ev["timestamp"],
            }
            computed = trace_ledger.compute_step_hash(expected_prev, p)
            if computed != ev.get("current_hash") or ev.get("previous_hash") != expected_prev:
                return {
                    "valid": False,
                    "status": "TRACE ALTERED",
                    "tampered_step": ev.get("sequence_index", i + 1),
                    "expected_hash": computed,
                    "received_hash": ev.get("current_hash"),
                    "details": f"Cryptographic divergence detected at step {ev.get('sequence_index', i + 1)}"
                }
            expected_prev = computed

        return {
            "valid": True,
            "status": "TRACE INTACT",
            "verified_steps": len(events),
            "tampered_step": None,
            "head_hash": expected_prev,
            "details": f"All {len(events)} events match cryptographic SHA-256 chained digests."
        }

    raise HTTPException(status_code=400, detail="Must provide request_id or events payload")
