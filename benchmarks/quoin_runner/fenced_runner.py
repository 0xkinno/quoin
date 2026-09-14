"""QUOIN Fenced Runner for controlled benchmark.

Full 4-plane architecture with generation fence, two-phase commit gate, and idempotent execution.
"""

from typing import Dict, Any, List
from quoin.agent.strands_agent import OperationalReasoningAgent
from quoin.kernel.fence import GenerationFence
from quoin.kernel.gate import TwoPhaseCommitGate
from quoin.effects.service import OperationalEffectService
from quoin.effects.idempotency import IdempotencyLedger

class QuoinFencedRunner:
    """Production QUOIN agent with deterministic generation fence."""

    def __init__(self, memory_reader, effect_service: OperationalEffectService, enable_llm: bool = False):
        self.memory_reader = memory_reader
        self.effect_service = effect_service
        self.agent = OperationalReasoningAgent(
            memory_reader_callable=lambda t: self.memory_reader(),
            enable_bedrock=enable_llm,
        )
        self.fence = GenerationFence()
        self.gate = TwoPhaseCommitGate(authority_reader=self.memory_reader)
        self.committed_executions: List[Dict[str, Any]] = []

    def execute_request(self, request_payload: Dict[str, Any], in_flight_cutover_fn=None) -> Dict[str, Any]:
        # Phase 1: Reasoning & Proposal
        proposal = self.agent.process_request(request_payload)

        # Snapshot evaluation against Generation Fence
        start_snapshot = self.memory_reader()
        eval_res = self.fence.evaluate_proposal(proposal, request_payload, start_snapshot)
        if not eval_res.allowed:
            return {"status": eval_res.status, "reason": eval_res.reason}

        receipt = eval_res.receipt

        # In-flight cutover occurs here (if specified in scenario)
        if in_flight_cutover_fn:
            in_flight_cutover_fn()

        # Phase 2: Commit Gate with Read-After-Write verification
        effect_parameters = {
            "requested_action": proposal.requested_action,
            "requested_value": proposal.requested_value,
            **proposal.parameters,
        }
        intended_effect = {
            "action": proposal.requested_action,
            "parameters": effect_parameters,
        }

        def execute_effect(permit):
            if proposal.requested_action == "apply_discount":
                return self.effect_service.apply_discount(
                    permit=permit,
                    request_id=proposal.request_id,
                    discount_amount=proposal.requested_value or 0.0,
                    client_tier=proposal.parameters.get("client_tier", "standard"),
                    invoice_id=proposal.parameters.get("invoice_id", "inv_0"),
                    parameters=effect_parameters,
                )
            else:
                return self.effect_service.issue_service_credit(
                    permit=permit,
                    request_id=proposal.request_id,
                    credit_amount=proposal.requested_value or 0.0,
                    account_id=proposal.parameters.get("client_id", "acc_0"),
                    reason=proposal.rationale,
                    parameters=effect_parameters,
                )

        commit_res = self.gate.commit(
            receipt=receipt,
            current_request_data=request_payload,
            current_proposal=proposal,
            intended_effect=intended_effect,
            effect_executor=execute_effect,
        )

        if commit_res.committed:
            self.committed_executions.append(commit_res.effect_result)
            return {"status": "COMMITTED", "permit": commit_res.permit.permit_id, "result": commit_res.effect_result}
        else:
            return {"status": commit_res.status, "error": commit_res.error}
