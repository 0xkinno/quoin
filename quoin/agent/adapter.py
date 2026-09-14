"""Proposal Adapter (Plane A -> Plane B).

Enforces strict boundary conversion from untrusted model reasoning to typed DecisionProposal.
"""

from typing import Any, Dict, Optional
from ..kernel.models import DecisionProposal

class ProposalAdapter:
    """Adapts and validates unstructured or structured agent model output into DecisionProposal."""

    @staticmethod
    def adapt(
        request_id: str,
        raw_output: Dict[str, Any],
        candidate_generation: int,
    ) -> DecisionProposal:
        """Convert agent tool call or json output to verified DecisionProposal."""
        action = raw_output.get("action") or raw_output.get("requested_action", "unknown_action")
        raw_val = raw_output.get("value") or raw_output.get("requested_value") or raw_output.get("amount")
        val = float(raw_val) if raw_val is not None else None
        rationale = str(raw_output.get("rationale") or raw_output.get("reasoning", "No rationale provided"))
        
        parameters = raw_output.get("parameters", {})
        if not parameters:
            # Gather extra context parameters
            for k, v in raw_output.items():
                if k not in ["action", "requested_action", "value", "requested_value", "amount", "rationale", "reasoning"]:
                    parameters[k] = v

        return DecisionProposal(
            request_id=request_id,
            requested_action=action,
            requested_value=val,
            rationale=rationale,
            candidate_policy_generation=candidate_generation,
            parameters=parameters,
        )
