import pytest
from datetime import datetime, timezone, timedelta
from quoin.effects.service import OperationalEffectService
from quoin.effects.idempotency import IdempotencyLedger
from quoin.kernel.models import ExecutionPermit
from quoin.kernel.hasher import CanonicalHasher

@pytest.fixture
def effect_service():
    return OperationalEffectService(idempotency_ledger=IdempotencyLedger())

def create_test_permit(action: str, params: dict, gen: int = 18):
    now = datetime.now(timezone.utc)
    effect_hash = CanonicalHasher.compute_effect_hash(action, params)
    permit_id = CanonicalHasher.compute_permit_id("rcpt_test", effect_hash)
    sig = CanonicalHasher.sign_permit(permit_id, "rcpt_test", effect_hash, gen)
    return ExecutionPermit(
        permit_id=permit_id,
        receipt_id="rcpt_test",
        request_id="req_test",
        policy_generation=gen,
        effect_hash=effect_hash,
        issued_at=now,
        expires_at=now + timedelta(minutes=5),
        kernel_signature=sig
    )

def test_single_execution_and_idempotent_deduplication(effect_service):
    params = {
        "requested_action": "apply_discount",
        "requested_value": 300.0,
        "client_tier": "gold",
        "invoice_id": "inv_123"
    }
    permit = create_test_permit("apply_discount", params)

    # First call: executes successfully
    res1 = effect_service.apply_discount(
        permit=permit,
        request_id="req_test",
        discount_amount=300.0,
        client_tier="gold",
        invoice_id="inv_123"
    )
    assert res1["status"] == "SUCCESS"
    assert effect_service.ledger.count() == 1

    # Second call (replay attempt with same permit): deduplicated!
    res2 = effect_service.apply_discount(
        permit=permit,
        request_id="req_test",
        discount_amount=300.0,
        client_tier="gold",
        invoice_id="inv_123"
    )
    assert res2["status"] == "DEDUPLICATED"
    assert res2["duplicate_attempt"] is True
    assert effect_service.ledger.count() == 1 # Still 1 execution!

def test_tampered_permit_rejected(effect_service):
    params = {
        "requested_action": "apply_discount",
        "requested_value": 300.0,
        "client_tier": "gold",
        "invoice_id": "inv_123"
    }
    permit = create_test_permit("apply_discount", params)

    # Attempt to use permit for different amount (tampering)
    with pytest.raises(ValueError, match="Permit effect hash mismatch"):
        effect_service.apply_discount(
            permit=permit,
            request_id="req_test",
            discount_amount=999.0, # Mismatch!
            client_tier="gold",
            invoice_id="inv_123"
        )
