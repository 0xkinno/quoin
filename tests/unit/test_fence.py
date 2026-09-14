import pytest
from datetime import datetime, timezone
from quoin.kernel.models import PolicyRule, PolicyRecord, AuthoritySnapshot, DecisionProposal
from quoin.kernel.fence import GenerationFence
from quoin.kernel.hasher import CanonicalHasher

@pytest.fixture
def sample_snapshot_g18():
    now = datetime(2026, 9, 14, 8, 0, 0, tzinfo=timezone.utc)
    policy = PolicyRecord(
        policy_id="pol_agency_v1",
        generation=18,
        version_hash="v18",
        effective_at=now,
        scope="discount",
        rules=[
            PolicyRule(rule_id="r_std", client_tier="standard", max_discount_amount=500.0, max_discount_percentage=10.0),
            PolicyRule(rule_id="r_gold", client_tier="gold", max_discount_amount=1000.0, max_discount_percentage=15.0),
        ]
    )
    p_hash = CanonicalHasher.compute_policy_hash(policy)
    return AuthoritySnapshot(
        policy_id="pol_agency_v1",
        generation=18,
        visible_at=now,
        source="agentcore_memory",
        retrieved_record_hash=p_hash,
        namespace="/quoin/agency/policy",
        policy_record=policy
    )

def test_generation_fence_matching_generation(sample_snapshot_g18):
    fence = GenerationFence()
    proposal = DecisionProposal(
        request_id="req_101",
        requested_action="apply_discount",
        requested_value=400.0,
        rationale="Client is eligible for 8% discount",
        candidate_policy_generation=18,
        parameters={"client_tier": "standard", "discount_percentage": 8.0}
    )
    req = {"client_id": "cust_1", "amount": 400.0, "tier": "standard"}

    res = fence.evaluate_proposal(proposal, req, sample_snapshot_g18)
    assert res.allowed is True
    assert res.status == "PERMITTED"
    assert res.receipt is not None
    assert res.receipt.policy_generation == 18

def test_generation_fence_stale_generation_blocked(sample_snapshot_g18):
    fence = GenerationFence()
    # Proposal evaluated under old generation G17
    proposal = DecisionProposal(
        request_id="req_102",
        requested_action="apply_discount",
        requested_value=1200.0, # Valid under G17 ($1500 limit), but G18 is active ($1000 limit)
        rationale="Allowing gold discount under G17",
        candidate_policy_generation=17,
        parameters={"client_tier": "gold"}
    )
    req = {"client_id": "cust_gold", "amount": 1200.0, "tier": "gold"}

    res = fence.evaluate_proposal(proposal, req, sample_snapshot_g18)
    assert res.allowed is False
    assert res.status == "FENCE_BLOCKED"
    assert "Policy Generation Mismatch" in res.reason
    assert res.receipt is None

def test_generation_fence_policy_amount_violation(sample_snapshot_g18):
    fence = GenerationFence()
    proposal = DecisionProposal(
        request_id="req_103",
        requested_action="apply_discount",
        requested_value=650.0, # Exceeds $500 standard limit under G18
        rationale="Trying to exceed standard limit",
        candidate_policy_generation=18,
        parameters={"client_tier": "standard", "discount_percentage": 13.0}
    )
    req = {"client_id": "cust_2", "amount": 650.0, "tier": "standard"}

    res = fence.evaluate_proposal(proposal, req, sample_snapshot_g18)
    assert res.allowed is False
    assert res.status == "POLICY_VIOLATION"
    assert "exceeds max allowable $500.0" in res.reason
