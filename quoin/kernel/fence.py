"""Generation Fence (Plane B).

Enforces strict policy generation matching and deterministic rule compliance.
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional
from .models import (
    DecisionProposal,
    AuthoritySnapshot,
    AuthorityReceipt,
    FenceEvaluationResult,
    PolicyRecord,
    PolicyRule,
)
from .hasher import CanonicalHasher

class GenerationFence:
    """Deterministic barrier preventing actions evaluated under stale policy generations."""

    def __init__(self, receipt_ttl_seconds: int = 60, kernel_version: str = "1.0.0"):
        self.receipt_ttl = timedelta(seconds=receipt_ttl_seconds)
        self.kernel_version = kernel_version

    def evaluate_proposal(
        self,
        proposal: DecisionProposal,
        request_data: Dict[str, Any],
        snapshot: AuthoritySnapshot,
    ) -> FenceEvaluationResult:
        """Evaluate a proposal against the generation fence and active policy snapshot."""
        now = datetime.now(timezone.utc)

        # 1. Primary Invariant: Generation Equality Check
        if proposal.candidate_policy_generation != snapshot.generation:
            return FenceEvaluationResult(
                allowed=False,
                status="FENCE_BLOCKED",
                reason=(
                    f"Policy Generation Mismatch: Proposal reasoned under G{proposal.candidate_policy_generation}, "
                    f"but active visible authority is G{snapshot.generation}. Action blocked by generation fence."
                ),
                current_generation=snapshot.generation,
                proposed_generation=proposal.candidate_policy_generation,
                snapshot=snapshot,
            )

        # 2. Policy Record Integrity Check
        if snapshot.policy_record:
            recomputed_policy_hash = CanonicalHasher.compute_policy_hash(snapshot.policy_record)
            if recomputed_policy_hash != snapshot.retrieved_record_hash:
                return FenceEvaluationResult(
                    allowed=False,
                    status="POLICY_INTEGRITY_TAMPER",
                    reason="Authority snapshot hash mismatch: Record content differs from retrieved digest.",
                    current_generation=snapshot.generation,
                    proposed_generation=proposal.candidate_policy_generation,
                    snapshot=snapshot,
                )

        # 3. Deterministic Policy Rule Compliance
        compliance_check = self._check_rule_compliance(proposal, snapshot.policy_record)
        if not compliance_check["allowed"]:
            return FenceEvaluationResult(
                allowed=False,
                status="POLICY_VIOLATION",
                reason=compliance_check["reason"],
                current_generation=snapshot.generation,
                proposed_generation=proposal.candidate_policy_generation,
                snapshot=snapshot,
            )

        # 4. Generate Cryptographic Authority Receipt
        request_hash = CanonicalHasher.compute_request_hash(request_data)
        proposal_hash = CanonicalHasher.compute_proposal_hash(proposal)
        policy_hash = snapshot.retrieved_record_hash
        snapshot_hash = CanonicalHasher.digest(snapshot)

        # Compute intended effect hash
        effect_parameters = {
            "requested_action": proposal.requested_action,
            "requested_value": proposal.requested_value,
            **proposal.parameters,
        }
        effect_hash = CanonicalHasher.compute_effect_hash(proposal.requested_action, effect_parameters)
        receipt_id = CanonicalHasher.compute_receipt_id(proposal.request_id, snapshot.generation, effect_hash)

        receipt = AuthorityReceipt(
            receipt_id=receipt_id,
            request_id=proposal.request_id,
            policy_id=snapshot.policy_id,
            policy_generation=snapshot.generation,
            policy_hash=policy_hash,
            request_hash=request_hash,
            proposal_hash=proposal_hash,
            authority_snapshot_hash=snapshot_hash,
            effect_hash=effect_hash,
            issued_at=now,
            expires_at=now + self.receipt_ttl,
            kernel_version=self.kernel_version,
            valid=True,
            reason="Complies with verified generation policy",
        )

        return FenceEvaluationResult(
            allowed=True,
            status="PERMITTED",
            reason=f"Proposal verified and fenced to Generation G{snapshot.generation}.",
            current_generation=snapshot.generation,
            proposed_generation=proposal.candidate_policy_generation,
            receipt=receipt,
            snapshot=snapshot,
        )

    def _check_rule_compliance(self, proposal: DecisionProposal, policy: Optional[PolicyRecord]) -> Dict[str, Any]:
        """Pure model-free deterministic rule evaluation."""
        if not policy:
            return {"allowed": True, "reason": "No explicit policy rules configured."}

        action = proposal.requested_action.lower()
        val = proposal.requested_value or 0.0
        client_tier = proposal.parameters.get("client_tier", "standard").lower()

        # Discount rule checking
        if "discount" in action:
            matching_rules = [
                r for r in policy.rules 
                if (r.client_tier is None or r.client_tier.lower() == client_tier)
            ]
            if not matching_rules:
                # Check general rules
                matching_rules = policy.rules

            for r in matching_rules:
                if r.max_discount_amount > 0 and val > r.max_discount_amount:
                    return {
                        "allowed": False,
                        "reason": f"Requested discount ${val} exceeds max allowable ${r.max_discount_amount} under G{policy.generation} for tier '{client_tier}'.",
                    }
                requested_pct = float(proposal.parameters.get("discount_percentage", 0.0))
                if r.max_discount_percentage > 0 and requested_pct > r.max_discount_percentage:
                    return {
                        "allowed": False,
                        "reason": f"Requested discount {requested_pct}% exceeds max allowable {r.max_discount_percentage}% under G{policy.generation}.",
                    }
                if r.requires_escalation:
                    return {
                        "allowed": False,
                        "reason": f"Action requires executive escalation under G{policy.generation}.",
                    }

        # Credit / Refund rule checking
        elif "refund" in action or "credit" in action:
            for r in policy.rules:
                if r.max_credit_amount > 0 and val > r.max_credit_amount:
                    return {
                        "allowed": False,
                        "reason": f"Requested credit ${val} exceeds allowable ceiling ${r.max_credit_amount} under G{policy.generation}.",
                    }

        return {"allowed": True, "reason": "Compliant"}
