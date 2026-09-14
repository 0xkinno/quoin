from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ..state import app_state
from quoin.kernel.models import DecisionProposal, AuthorityReceipt
from quoin.kernel.hasher import CanonicalHasher

router = APIRouter(prefix="/api/requests", tags=["Requests"])

class RequestEvaluatePayload(BaseModel):
    request_id: str
    tenant_id: str = "agency_operations"
    client_id: str = "cust_01"
    client_tier: str = "gold"
    amount: float = 700.0
    action: str = "apply_discount"
    invoice_id: str = "inv_409"
    discount_percentage: float = 14.0

class RequestCommitPayload(BaseModel):
    receipt: Dict[str, Any]
    request_payload: Dict[str, Any]
    proposal: Dict[str, Any]
    intended_effect: Optional[Dict[str, Any]] = None

@router.post("/evaluate")
def evaluate_request(payload: Dict[str, Any]):
    req_dict = payload
    tenant_id = payload.get("tenant_id", "agency_operations")

    # 1. Agent processes request
    proposal = app_state.agent.process_request(req_dict)

    # 2. Kernel Generation Fence evaluates proposal
    snapshot = app_state.memory.get_active_snapshot(tenant_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="No active policy snapshot available")

    eval_result = app_state.fence.evaluate_proposal(proposal, req_dict, snapshot)
    app_state.verification_ledger.record_evaluation(eval_result)

    response = {
        "allowed": eval_result.allowed,
        "status": eval_result.status,
        "reason": eval_result.reason,
        "current_generation": eval_result.current_generation,
        "proposed_generation": eval_result.proposed_generation,
        "proposal": proposal.model_dump(),
        "receipt": eval_result.receipt.model_dump() if eval_result.receipt else None,
    }
    return response

@router.post("/commit")
def commit_request(payload: RequestCommitPayload):
    tenant_id = payload.request_payload.get("tenant_id", "agency_operations")
    receipt = AuthorityReceipt(**payload.receipt)
    proposal = DecisionProposal(**payload.proposal)
    req_dict = payload.request_payload

    effect_parameters = {
        "requested_action": proposal.requested_action,
        "requested_value": proposal.requested_value,
        **proposal.parameters
    }
    intended_effect = payload.intended_effect or {
        "action": proposal.requested_action,
        "parameters": effect_parameters
    }

    def effect_executor(permit):
        if proposal.requested_action == "apply_discount":
            return app_state.effect_service.apply_discount(
                permit=permit,
                request_id=proposal.request_id,
                discount_amount=proposal.requested_value or 0.0,
                client_tier=proposal.parameters.get("client_tier", "standard"),
                invoice_id=proposal.parameters.get("invoice_id", "inv_unknown"),
                parameters=effect_parameters,
            )
        else:
            return app_state.effect_service.issue_service_credit(
                permit=permit,
                request_id=proposal.request_id,
                credit_amount=proposal.requested_value or 0.0,
                account_id=proposal.parameters.get("client_id", "acc_unknown"),
                reason=proposal.rationale,
                parameters=effect_parameters,
            )

    commit_res = app_state.gate.commit(
        receipt=receipt,
        current_request_data=req_dict,
        current_proposal=proposal,
        intended_effect=intended_effect,
        effect_executor=effect_executor
    )
    app_state.verification_ledger.record_commit(commit_res)

    return {
        "committed": commit_res.committed,
        "status": commit_res.status,
        "permit": commit_res.permit.model_dump() if commit_res.permit else None,
        "effect_result": commit_res.effect_result,
        "error": commit_res.error,
        "audit_trail": commit_res.audit_trail
    }
