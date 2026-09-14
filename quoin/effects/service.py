"""Plane D: Professional operational actions service.

Executes consequential actions strictly guarded by verified ExecutionPermits.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from ..kernel.models import ExecutionPermit
from ..kernel.hasher import CanonicalHasher
from .idempotency import IdempotencyLedger, ExecutionRecord

class OperationalEffectService:
    """Dispatches and commits business side-effects under cryptographic permits."""

    def __init__(self, idempotency_ledger: Optional[IdempotencyLedger] = None):
        self.ledger = idempotency_ledger or IdempotencyLedger()

    def _verify_permit(self, permit: ExecutionPermit, expected_effect_hash: str) -> None:
        """Verify that the permit is genuine, unexpired, and matches intended effect."""
        now = datetime.now(timezone.utc)
        if now > permit.expires_at:
            raise ValueError(f"Permit {permit.permit_id} is expired.")

        expected_sig = CanonicalHasher.sign_permit(
            permit.permit_id,
            permit.receipt_id,
            permit.effect_hash,
            permit.policy_generation,
        )
        if permit.kernel_signature != expected_sig:
            raise ValueError(f"Invalid kernel signature on permit {permit.permit_id}.")

        if permit.effect_hash != expected_effect_hash:
            raise ValueError("Permit effect hash mismatch with intended action.")

    def apply_discount(
        self,
        permit: ExecutionPermit,
        request_id: str,
        discount_amount: float,
        client_tier: str,
        invoice_id: str = "inv_current",
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Apply a commercial discount override to an invoice."""
        if parameters is not None:
            effect_params = parameters
        else:
            effect_params = {
                "requested_action": "apply_discount",
                "requested_value": discount_amount,
                "client_tier": client_tier,
                "invoice_id": invoice_id,
            }
        effect_hash = CanonicalHasher.compute_effect_hash("apply_discount", effect_params)
        self._verify_permit(permit, effect_hash)

        existing = self.ledger.get_existing(permit.permit_id, request_id, effect_hash)
        if existing:
            return {
                "status": "DEDUPLICATED",
                "message": "Discount already applied under this permit.",
                "record": existing.model_dump(),
                "duplicate_attempt": True,
            }

        execution_payload = {
            "action": "apply_discount",
            "request_id": request_id,
            "discount_amount": discount_amount,
            "client_tier": client_tier,
            "invoice_id": invoice_id,
            "generation_bound": permit.policy_generation,
            "permit_id": permit.permit_id,
            "committed_at": datetime.now(timezone.utc).isoformat(),
        }

        rec = self.ledger.record_execution(
            permit_id=permit.permit_id,
            receipt_id=permit.receipt_id,
            request_id=request_id,
            generation=permit.policy_generation,
            effect_hash=effect_hash,
            result=execution_payload,
        )

        return {
            "status": "SUCCESS",
            "action": "apply_discount",
            "discount_amount": discount_amount,
            "execution_id": rec.permit_id,
            "record": rec.model_dump(),
        }

    def issue_service_credit(
        self,
        permit: ExecutionPermit,
        request_id: str,
        credit_amount: float,
        account_id: str,
        reason: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Issue client service credit."""
        if parameters is not None:
            effect_params = parameters
        else:
            effect_params = {
                "requested_action": "issue_service_credit",
                "requested_value": credit_amount,
                "account_id": account_id,
                "reason": reason,
            }
        effect_hash = CanonicalHasher.compute_effect_hash("issue_service_credit", effect_params)
        self._verify_permit(permit, effect_hash)

        existing = self.ledger.get_existing(permit.permit_id, request_id, effect_hash)
        if existing:
            return {
                "status": "DEDUPLICATED",
                "message": "Credit already issued under this permit.",
                "record": existing.model_dump(),
                "duplicate_attempt": True,
            }

        execution_payload = {
            "action": "issue_service_credit",
            "request_id": request_id,
            "credit_amount": credit_amount,
            "account_id": account_id,
            "reason": reason,
            "generation_bound": permit.policy_generation,
            "permit_id": permit.permit_id,
            "committed_at": datetime.now(timezone.utc).isoformat(),
        }

        rec = self.ledger.record_execution(
            permit_id=permit.permit_id,
            receipt_id=permit.receipt_id,
            request_id=request_id,
            generation=permit.policy_generation,
            effect_hash=effect_hash,
            result=execution_payload,
        )

        return {
            "status": "SUCCESS",
            "action": "issue_service_credit",
            "credit_amount": credit_amount,
            "execution_id": rec.permit_id,
            "record": rec.model_dump(),
        }
