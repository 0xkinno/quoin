"""Strands Reasoning Agent (Plane A).

Integrates the Strands Agents SDK for operational request classification, policy retrieval, and proposal generation.
Strictly isolated from authority commit gates and side-effect dispatch.
"""

from typing import Dict, Any, Optional
from .adapter import ProposalAdapter
from .tools import query_policy_context, formulate_proposal
from ..kernel.models import DecisionProposal

class OperationalReasoningAgent:
    """Strands-powered reasoning agent formulating proposals for professional operations."""

    def __init__(self, memory_reader_callable, model_id: Optional[str] = None):
        self.memory_reader = memory_reader_callable
        self.model_id = model_id
        self._strands_agent = None

        # Attempt to initialize live Strands agent if model_id is configured
        if self.model_id:
            try:
                from strands import Agent
                self._strands_agent = Agent(
                    model=self.model_id,
                    system_prompt=(
                        "You are an operational assistant analyzing client requests against company policy. "
                        "Read current policy context and formulate a structured proposal. "
                        "You CANNOT execute actions directly."
                    ),
                )
            except Exception as e:
                # Running in local simulation mode
                self._strands_agent = None

    def process_request(self, request_payload: Dict[str, Any]) -> DecisionProposal:
        """Process an operational request and produce a candidate DecisionProposal."""
        request_id = request_payload["request_id"]
        tenant_id = request_payload.get("tenant_id", "agency_operations")
        action = request_payload.get("action", "apply_discount")
        amount = float(request_payload.get("amount", 0.0))
        client_tier = request_payload.get("client_tier", "standard")

        # Step 1: Query currently visible candidate policy
        policy_context = query_policy_context(tenant_id, self.memory_reader)
        observed_gen = policy_context.get("generation", 0)

        # Step 2: Formulate candidate proposal based on business logic
        raw_proposal = formulate_proposal(
            request_id=request_id,
            action=action,
            amount=amount,
            rationale=f"Evaluated client request for ${amount} discount under visible policy G{observed_gen}.",
            observed_generation=observed_gen,
            client_tier=client_tier,
            additional_params={
                "client_id": request_payload.get("client_id", "client_unknown"),
                "invoice_id": request_payload.get("invoice_id", "inv_unknown"),
                "discount_percentage": request_payload.get("discount_percentage", 0.0),
            },
        )

        # Step 3: Strictly adapt output across Plane A -> Plane B boundary
        proposal = ProposalAdapter.adapt(
            request_id=request_id,
            raw_output=raw_proposal,
            candidate_generation=observed_gen,
        )

        return proposal
