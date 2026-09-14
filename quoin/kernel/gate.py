"""Two-Phase Commit Gate (Plane B).

Enforces read-after-write re-verification and issues execution permits immediately before effect execution.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Callable
from .models import (
    AuthorityReceipt,
    ExecutionPermit,
    CommitResult,
    AuthoritySnapshot,
    DecisionProposal,
)
from .hasher import CanonicalHasher

class TwoPhaseCommitGate:
    """Compare-and-swap authority gate executing side effects only under valid generation bindings."""

    def __init__(
        self,
        authority_reader: Optional[Callable[[], AuthoritySnapshot]] = None,
        authority_ledger: Optional[Any] = None,
    ):
        self.authority_reader = authority_reader
        self.authority_ledger = authority_ledger
        self.invalidated_receipts: set[str] = set()

    def evaluate_commit(
        self,
        receipt: AuthorityReceipt,
        current_request_data: Dict[str, Any],
        current_proposal: DecisionProposal,
        current_snapshot: Optional[AuthoritySnapshot] = None,
        intended_effect: Optional[Dict[str, Any]] = None,
    ) -> CommitResult:
        """Evaluate Phase 2 commit predicates without dispatching execution."""
        now = datetime.now(timezone.utc)
        receipt_id = receipt.receipt_id

        # 0. Check receipt cancellation
        if not receipt.valid or receipt_id in self.invalidated_receipts:
            return CommitResult(
                committed=False,
                status="ABORTED_INVALID_RECEIPT",
                error=f"Receipt {receipt_id} has been invalidated or cancelled.",
                audit_trail={"receipt_id": receipt_id, "aborted_at": now.isoformat()},
            )

        # 1. Expiration check
        if now > receipt.expires_at:
            self.invalidated_receipts.add(receipt_id)
            return CommitResult(
                committed=False,
                status="ABORTED_EXPIRED_RECEIPT",
                error=f"Receipt {receipt_id} expired at {receipt.expires_at.isoformat()} (Current: {now.isoformat()}).",
                audit_trail={"receipt_id": receipt_id, "expired_at": receipt.expires_at.isoformat()},
            )

        # 2. Phase 2 Read-After-Write: Snapshot lookup
        snapshot = current_snapshot or (self.authority_reader() if self.authority_reader else None)
        if snapshot is None:
            return CommitResult(
                committed=False,
                status="ABORTED_NO_ACTIVE_AUTHORITY",
                error="No active authority snapshot available for verification.",
                audit_trail={"receipt_id": receipt_id, "aborted_at": now.isoformat()},
            )

        # 3. Policy ID / Cross-tenant check
        if receipt.policy_id != snapshot.policy_id:
            self.invalidated_receipts.add(receipt_id)
            return CommitResult(
                committed=False,
                status="ABORTED_CROSS_TENANT_MISMATCH",
                error=f"Cross-tenant policy ID mismatch: Receipt policy_id '{receipt.policy_id}' != snapshot policy_id '{snapshot.policy_id}'.",
                audit_trail={"receipt_policy_id": receipt.policy_id, "snapshot_policy_id": snapshot.policy_id},
            )

        # 4. Generation Match Check (The Core Fence)
        if receipt.policy_generation != snapshot.generation:
            self.invalidated_receipts.add(receipt_id)
            return CommitResult(
                committed=False,
                status="ABORTED_STALE_GENERATION",
                error=(
                    f"Generation Race Detected: Receipt bound to G{receipt.policy_generation}, "
                    f"but active visible authority advanced to G{snapshot.generation}. Aborting commit."
                ),
                audit_trail={
                    "receipt_generation": receipt.policy_generation,
                    "active_generation": snapshot.generation,
                    "aborted_at": now.isoformat(),
                },
            )

        # 5. Policy Hash Check
        if receipt.policy_hash != snapshot.retrieved_record_hash:
            self.invalidated_receipts.add(receipt_id)
            return CommitResult(
                committed=False,
                status="ABORTED_POLICY_HASH_MISMATCH",
                error="Active policy digest differs from authority receipt policy digest.",
                audit_trail={"receipt_hash": receipt.policy_hash, "active_hash": snapshot.retrieved_record_hash},
            )

        # 6. Request Mutation / Tamper Check
        current_req_hash = CanonicalHasher.compute_request_hash(current_request_data)
        if receipt.request_hash != current_req_hash:
            self.invalidated_receipts.add(receipt_id)
            return CommitResult(
                committed=False,
                status="ABORTED_TAMPER_REQUEST",
                error="Request payload was mutated after authority receipt issuance.",
                audit_trail={"receipt_req_hash": receipt.request_hash, "current_req_hash": current_req_hash},
            )

        # 7. Proposal Mutation / Tamper Check
        current_prop_hash = CanonicalHasher.compute_proposal_hash(current_proposal)
        if receipt.proposal_hash != current_prop_hash:
            self.invalidated_receipts.add(receipt_id)
            return CommitResult(
                committed=False,
                status="ABORTED_TAMPER_PROPOSAL",
                error="Decision proposal was mutated after authority receipt issuance.",
                audit_trail={"receipt_prop_hash": receipt.proposal_hash, "current_prop_hash": current_prop_hash},
            )

        # 8. Intended Effect Hash Check (if given)
        if intended_effect is not None:
            current_effect_hash = CanonicalHasher.compute_effect_hash(
                intended_effect["action"],
                intended_effect.get("parameters", {}),
            )
            if receipt.effect_hash != current_effect_hash:
                self.invalidated_receipts.add(receipt_id)
                return CommitResult(
                    committed=False,
                    status="ABORTED_TAMPER_EFFECT",
                    error="Intended effect does not match receipt effect digest.",
                    audit_trail={"receipt_effect_hash": receipt.effect_hash, "current_effect_hash": current_effect_hash},
                )

        return CommitResult(
            committed=True,
            status="COMMITTED",
            audit_trail={"receipt_id": receipt_id, "generation": snapshot.generation, "verified_at": now.isoformat()},
        )

    def commit(
        self,
        receipt: AuthorityReceipt,
        current_request_data: Dict[str, Any],
        current_proposal: DecisionProposal,
        intended_effect: Dict[str, Any],
        effect_executor: Callable[[ExecutionPermit], Dict[str, Any]],
        current_snapshot: Optional[AuthoritySnapshot] = None,
    ) -> CommitResult:
        """Execute Phase 2 of Two-Phase Authority."""
        now = datetime.now(timezone.utc)
        receipt_id = receipt.receipt_id

        eval_res = self.evaluate_commit(
            receipt=receipt,
            current_request_data=current_request_data,
            current_proposal=current_proposal,
            current_snapshot=current_snapshot,
            intended_effect=intended_effect,
        )
        if not eval_res.committed:
            return eval_res

        snapshot = current_snapshot or (self.authority_reader() if self.authority_reader else None)
        current_effect_hash = CanonicalHasher.compute_effect_hash(
            intended_effect["action"],
            intended_effect.get("parameters", {}),
        )

        permit_id = CanonicalHasher.compute_permit_id(receipt_id, current_effect_hash)

        # Check atomic ledger for single-use permit consumption
        if self.authority_ledger and self.authority_ledger.is_permit_consumed(permit_id):
            return CommitResult(
                committed=False,
                status="ABORTED_PERMIT_REPLAY",
                error=f"Execution permit {permit_id} has already been consumed.",
                audit_trail={"permit_id": permit_id, "aborted_at": now.isoformat()},
            )

        signature = CanonicalHasher.sign_permit(permit_id, receipt_id, current_effect_hash, snapshot.generation)

        permit = ExecutionPermit(
            permit_id=permit_id,
            receipt_id=receipt_id,
            request_id=receipt.request_id,
            policy_generation=snapshot.generation,
            effect_hash=current_effect_hash,
            issued_at=now,
            expires_at=receipt.expires_at,
            kernel_signature=signature,
        )

        # 9. Execute Idempotent Effect (Plane D)
        try:
            effect_result = effect_executor(permit)
            if self.authority_ledger:
                self.authority_ledger.consume_permit_atomic(
                    permit_id=permit_id,
                    request_id=receipt.request_id,
                    epoch=snapshot.generation,
                    policy_hash=receipt.policy_hash,
                    effect_hash=current_effect_hash,
                )
            return CommitResult(
                committed=True,
                status="COMMITTED",
                permit=permit,
                effect_result=effect_result,
                audit_trail={
                    "permit_id": permit_id,
                    "generation": snapshot.generation,
                    "committed_at": now.isoformat(),
                },
            )
        except Exception as e:
            return CommitResult(
                committed=False,
                status="EFFECT_EXECUTION_FAILURE",
                error=f"Execution service failed: {str(e)}",
                audit_trail={"permit_id": permit_id, "error": str(e)},
            )
