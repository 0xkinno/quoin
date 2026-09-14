import pytest
from datetime import datetime, timezone
from quoin.kernel.models import PolicyRule, PolicyRecord, DecisionProposal
from quoin.kernel.hasher import CanonicalHasher

def test_canonical_hasher_consistency():
    now = datetime(2026, 9, 14, 8, 0, 0, tzinfo=timezone.utc)
    p1 = PolicyRecord(
        policy_id="pol_test_1",
        generation=17,
        version_hash="pending",
        effective_at=now,
        scope="discount",
        rules=[PolicyRule(rule_id="r1", max_discount_amount=500.0)]
    )
    p2 = PolicyRecord(
        policy_id="pol_test_1",
        generation=17,
        version_hash="different_ignored",
        effective_at=now,
        scope="discount",
        rules=[PolicyRule(rule_id="r1", max_discount_amount=500.0)]
    )
    # Excludes version_hash from policy content hash
    h1 = CanonicalHasher.compute_policy_hash(p1)
    h2 = CanonicalHasher.compute_policy_hash(p2)
    assert h1 == h2
    assert len(h1) == 64

def test_request_and_proposal_hash():
    req1 = {"client_id": "c1", "amount": 250.0, "tier": "standard"}
    req2 = {"tier": "standard", "amount": 250.0, "client_id": "c1"}
    # Key ordering must not affect digest
    assert CanonicalHasher.compute_request_hash(req1) == CanonicalHasher.compute_request_hash(req2)
