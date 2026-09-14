"""Typed agent tools for Strands reasoning plane.

NOTE: Tools provide ONLY read context and proposal formulation.
They do NOT have access to kernel commit gates or side-effect dispatch.
"""

from typing import Dict, Any, Optional

def query_policy_context(tenant_id: str, memory_reader_callable) -> Dict[str, Any]:
    """Retrieve currently visible candidate policy for reasoning context."""
    snapshot = memory_reader_callable(tenant_id)
    if not snapshot or not snapshot.policy_record:
        return {
            "status": "NOT_FOUND",
            "message": f"No active policy found for tenant {tenant_id}",
            "generation": 0,
        }

    return {
        "status": "VISIBLE",
        "policy_id": snapshot.policy_id,
        "generation": snapshot.generation,
        "scope": snapshot.policy_record.scope,
        "rules": [r.model_dump() for r in snapshot.policy_record.rules],
        "visible_at": snapshot.visible_at.isoformat(),
    }

def formulate_proposal(
    request_id: str,
    action: str,
    amount: Optional[float],
    rationale: str,
    observed_generation: int,
    client_tier: str = "standard",
    additional_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Format structured operational action proposal."""
    params = additional_params or {}
    params["client_tier"] = client_tier
    return {
        "request_id": request_id,
        "requested_action": action,
        "requested_value": amount,
        "rationale": rationale,
        "candidate_policy_generation": observed_generation,
        "parameters": params,
    }
