import pytest
from datetime import datetime, timezone, timedelta
from quoin.kernel.models import PolicyRule, PolicyRecord, AuthoritySnapshot, DecisionProposal
from quoin.kernel.fence import GenerationFence
from quoin.kernel.gate import TwoPhaseCommitGate
from quoin.kernel.hasher import CanonicalHasher

def create_snapshot(gen: int, max_discount: float = 1000.0):
    now = datetime(2026, 9, 14, 8, 0, 0, tzinfo=timezone.utc)
    policy = PolicyRecord(
        policy_id="pol_ops",
        generation=gen,
        version_hash=f"v{gen}",
        effective_at=now,
        scope="discount",
        rules=[PolicyRule(rule_id="r1", client_tier="standard", max_discount_amount=max_discount)]
    )
    p_hash = CanonicalHasher.compute_policy_hash(policy)
    return AuthoritySnapshot(
        policy_id="pol_ops",
        generation=gen,
        visible_at=now,
        source="memory",
        retrieved_record_hash=p_hash,
        namespace="/quoin/policy",
        policy_record=policy
    )

def test_two_phase_commit_happy_path():
    snapshot = create_snapshot(18, 500.0)
    current_snapshot = snapshot
    gate = TwoPhaseCommitGate(authority_reader=lambda: current_snapshot)
    fence = GenerationFence()

    req = {"request_id": "r1", "client_tier": "standard", "amount": 350.0}
    proposal = DecisionProposal(
        request_id="r1",
        requested_action="apply_discount",
        requested_value=350.0,
        rationale="Within limits",
        candidate_policy_generation=18,
        parameters={"client_tier": "standard", "invoice_id": "inv_1"}
    )
    res = fence.evaluate_proposal(proposal, req, snapshot)
    assert res.allowed is True
    receipt = res.receipt

    # Side effect execution mock
    executed = []
    def mock_effect(permit):
        executed.append(permit.permit_id)
        return {"result": "APPLIED", "permit": permit.permit_id}

    intended_effect = {
        "action": "apply_discount",
        "parameters": {"requested_action": "apply_discount", "requested_value": 350.0, "client_tier": "standard", "invoice_id": "inv_1"}
    }

    commit_res = gate.commit(receipt, req, proposal, intended_effect, mock_effect)
    assert commit_res.committed is True
    assert commit_res.status == "COMMITTED"
    assert len(executed) == 1

def test_two_phase_commit_in_flight_generation_race():
    # Proposal evaluated under G17
    snapshot_g17 = create_snapshot(17, 1500.0)
    current_snapshot = snapshot_g17
    gate = TwoPhaseCommitGate(authority_reader=lambda: current_snapshot)
    fence = GenerationFence()

    req = {"request_id": "r2", "client_tier": "standard", "amount": 800.0}
    proposal = DecisionProposal(
        request_id="r2",
        requested_action="apply_discount",
        requested_value=800.0,
        rationale="Allowed under G17",
        candidate_policy_generation=17,
        parameters={"client_tier": "standard"}
    )
    eval_res = fence.evaluate_proposal(proposal, req, snapshot_g17)
    assert eval_res.allowed is True
    receipt = eval_res.receipt

    # NOW: POLICY CUTOVER OCCURS WHILE REQUEST IS IN-FLIGHT!
    # G18 activates with lower limit ($500 limit instead of $1500)
    current_snapshot = create_snapshot(18, 500.0)

    executed = []
    def mock_effect(permit):
        executed.append(permit.permit_id)
        return {"result": "APPLIED"}

    intended_effect = {
        "action": "apply_discount",
        "parameters": {"requested_action": "apply_discount", "requested_value": 800.0, "client_tier": "standard"}
    }

    # Commit gate MUST detect generation race and ABORT!
    commit_res = gate.commit(receipt, req, proposal, intended_effect, mock_effect)
    assert commit_res.committed is False
    assert commit_res.status == "ABORTED_STALE_GENERATION"
    assert "Generation Race Detected" in commit_res.error
    assert len(executed) == 0 # Zero side effects executed!

def test_two_phase_commit_tamper_detection():
    snapshot = create_snapshot(18, 1000.0)
    gate = TwoPhaseCommitGate(authority_reader=lambda: snapshot)
    fence = GenerationFence()

    req = {"request_id": "r3", "amount": 200.0}
    proposal = DecisionProposal(
        request_id="r3",
        requested_action="apply_discount",
        requested_value=200.0,
        rationale="ok",
        candidate_policy_generation=18
    )
    res = fence.evaluate_proposal(proposal, req, snapshot)
    receipt = res.receipt

    # Tamper request after receipt: change 200 to 900
    tampered_req = {"request_id": "r3", "amount": 900.0}
    intended_effect = {
        "action": "apply_discount",
        "parameters": {"requested_action": "apply_discount", "requested_value": 200.0}
    }

    commit_res = gate.commit(receipt, tampered_req, proposal, intended_effect, lambda p: {})
    assert commit_res.committed is False
    assert commit_res.status == "ABORTED_TAMPER_REQUEST"
