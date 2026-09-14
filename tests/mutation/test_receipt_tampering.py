import pytest
from datetime import datetime, timezone
from quoin.kernel.models import PolicyRule, PolicyRecord, AuthoritySnapshot, DecisionProposal
from quoin.kernel.fence import GenerationFence
from quoin.kernel.gate import TwoPhaseCommitGate
from quoin.kernel.hasher import CanonicalHasher

def create_valid_receipt_setup():
    now = datetime(2026, 9, 14, 8, 0, 0, tzinfo=timezone.utc)
    policy = PolicyRecord(
        policy_id="pol_ops",
        generation=18,
        version_hash="v18",
        effective_at=now,
        scope="discount",
        rules=[PolicyRule(rule_id="r1", max_discount_amount=1000.0)]
    )
    p_hash = CanonicalHasher.compute_policy_hash(policy)
    snapshot = AuthoritySnapshot(
        policy_id="pol_ops",
        generation=18,
        visible_at=now,
        source="memory",
        retrieved_record_hash=p_hash,
        namespace="/quoin/policy",
        policy_record=policy
    )
    req = {"request_id": "req_mut", "amount": 400.0}
    proposal = DecisionProposal(
        request_id="req_mut",
        requested_action="apply_discount",
        requested_value=400.0,
        rationale="Valid proposal",
        candidate_policy_generation=18
    )
    fence = GenerationFence()
    res = fence.evaluate_proposal(proposal, req, snapshot)
    return snapshot, req, proposal, res.receipt

def test_mutated_receipt_fields_blocked():
    snapshot, req, proposal, receipt = create_valid_receipt_setup()

    intended_effect = {
        "action": "apply_discount",
        "parameters": {"requested_action": "apply_discount", "requested_value": 400.0}
    }

    # 1. Mutate policy hash (tested with dedicated gate)
    gate1 = TwoPhaseCommitGate(authority_reader=lambda: snapshot)
    bad_receipt_1 = receipt.model_copy(update={"policy_hash": "deadbeef" * 8})
    res1 = gate1.commit(bad_receipt_1, req, proposal, intended_effect, lambda p: {})
    assert res1.committed is False
    assert res1.status == "ABORTED_POLICY_HASH_MISMATCH"

    # 2. Mutate proposal hash (tested with dedicated gate)
    gate2 = TwoPhaseCommitGate(authority_reader=lambda: snapshot)
    bad_receipt_2 = receipt.model_copy(update={"proposal_hash": "baadf00d" * 8})
    res2 = gate2.commit(bad_receipt_2, req, proposal, intended_effect, lambda p: {})
    assert res2.committed is False
    assert res2.status == "ABORTED_TAMPER_PROPOSAL"

    # 3. Mutate generation in receipt (tested with dedicated gate)
    gate3 = TwoPhaseCommitGate(authority_reader=lambda: snapshot)
    bad_receipt_3 = receipt.model_copy(update={"policy_generation": 19})
    res3 = gate3.commit(bad_receipt_3, req, proposal, intended_effect, lambda p: {})
    assert res3.committed is False
    assert res3.status == "ABORTED_STALE_GENERATION"

def test_invalidated_receipt_cannot_be_reused():
    snapshot, req, proposal, receipt = create_valid_receipt_setup()
    gate = TwoPhaseCommitGate(authority_reader=lambda: snapshot)

    intended_effect = {
        "action": "apply_discount",
        "parameters": {"requested_action": "apply_discount", "requested_value": 400.0}
    }

    # First attempt fails due to policy mismatch
    bad_receipt = receipt.model_copy(update={"policy_hash": "deadbeef" * 8})
    res1 = gate.commit(bad_receipt, req, proposal, intended_effect, lambda p: {})
    assert res1.committed is False

    # Second attempt with original receipt must be permanently ABORTED_INVALID_RECEIPT
    res2 = gate.commit(receipt, req, proposal, intended_effect, lambda p: {})
    assert res2.committed is False
    assert res2.status == "ABORTED_INVALID_RECEIPT"
