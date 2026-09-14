"""Adversarial Break Campaign Suite (Phase 6).

Implements all 13 attack classes specified in QUOIN_INSTRUCTION.md section 11.
"""

import pytest
import time
from datetime import datetime, timezone, timedelta
from quoin.kernel.models import PolicyRule, PolicyRecord, AuthoritySnapshot, DecisionProposal
from quoin.kernel.fence import GenerationFence
from quoin.kernel.gate import TwoPhaseCommitGate
from quoin.kernel.hasher import CanonicalHasher
from quoin.effects.service import OperationalEffectService
from quoin.effects.idempotency import IdempotencyLedger
from quoin.memory.local_simulator import LocalMemorySimulator

def helper_create_policy(gen: int, max_disc: float = 1000.0, rules=None) -> PolicyRecord:
    now = datetime(2026, 9, 14, 8, 0, 0, tzinfo=timezone.utc)
    rules_list = rules or [
        PolicyRule(rule_id=f"r_g{gen}", client_tier="standard", max_discount_amount=max_disc)
    ]
    return PolicyRecord(
        policy_id="pol_commercial",
        generation=gen,
        version_hash=f"v_hash_{gen}",
        effective_at=now,
        scope="discount",
        rules=rules_list,
    )

def test_attack_a_accepted_but_not_visible():
    """Attack A: Policy G18 accepted, but not yet visible. Agent attempts G17 action under G18 fence -> BLOCK."""
    sim = LocalMemorySimulator(default_visibility_lag_seconds=0.5)
    p17 = helper_create_policy(17, max_disc=1500.0)
    sim.ingest_policy("agency_a", p17, visibility_lag=0.0)
    sim.force_make_visible("agency_a")

    # Ingest G18 with 0.5s lag
    p18 = helper_create_policy(18, max_disc=500.0)
    sim.ingest_policy("agency_a", p18, visibility_lag=0.5)

    # Immediately attempt G17 action claiming G18
    fence = GenerationFence()
    snapshot = sim.retrieve_policy_snapshot("agency_a") # Still returns G17!
    proposal = DecisionProposal(
        request_id="att_a",
        requested_action="apply_discount",
        requested_value=1200.0,
        rationale="Claiming to execute under G18",
        candidate_policy_generation=18, # Claims G18
    )
    res = fence.evaluate_proposal(proposal, {"amount": 1200.0}, snapshot)
    # Fenced because snapshot is still G17 while proposal claimed G18
    assert res.allowed is False
    assert res.status == "FENCE_BLOCKED"

def test_attack_b_visible_but_stale_session():
    """Attack B: Long-running session has G17 in working memory, but store now has G18 -> BLOCK."""
    sim = LocalMemorySimulator()
    p17 = helper_create_policy(17, max_disc=1500.0)
    sim.ingest_policy("agency_b", p17, visibility_lag=0.0)
    sim.force_make_visible("agency_b")

    # Session evaluated proposal under G17
    fence = GenerationFence()
    snap_g17 = sim.retrieve_policy_snapshot("agency_b")
    proposal_g17 = DecisionProposal(
        request_id="att_b",
        requested_action="apply_discount",
        requested_value=1400.0,
        rationale="Old session context",
        candidate_policy_generation=17
    )
    res = fence.evaluate_proposal(proposal_g17, {"amount": 1400.0}, snap_g17)
    receipt_g17 = res.receipt
    assert receipt_g17 is not None

    # Memory now advances to G18
    p18 = helper_create_policy(18, max_disc=800.0)
    sim.ingest_policy("agency_b", p18, visibility_lag=0.0)
    sim.force_make_visible("agency_b")

    # Commit gate re-reads active authority: sees G18, blocks G17 receipt
    gate = TwoPhaseCommitGate(authority_reader=lambda: sim.retrieve_policy_snapshot("agency_b"))
    intended_effect = {
        "action": "apply_discount",
        "parameters": {"requested_action": "apply_discount", "requested_value": 1400.0}
    }
    commit_res = gate.commit(receipt_g17, {"amount": 1400.0}, proposal_g17, intended_effect, lambda p: {})
    assert commit_res.committed is False
    assert commit_res.status == "ABORTED_STALE_GENERATION"

def test_attack_c_generation_race():
    """Attack C: R1 starts under G17, policy changes to G18 during flight, R1 commits -> REJECTED."""
    p17 = helper_create_policy(17, max_disc=1000.0)
    snap_g17 = AuthoritySnapshot(
        policy_id="pol_c", generation=17, visible_at=datetime.now(timezone.utc), source="mem",
        retrieved_record_hash=CanonicalHasher.compute_policy_hash(p17), namespace="/quoin/c/policy", policy_record=p17
    )
    fence = GenerationFence()
    proposal = DecisionProposal(request_id="att_c", requested_action="apply_discount", requested_value=900.0, rationale="G17", candidate_policy_generation=17)
    res = fence.evaluate_proposal(proposal, {"amount": 900.0}, snap_g17)
    receipt = res.receipt

    # Race: New policy G18 activates immediately
    p18 = helper_create_policy(18, max_disc=500.0)
    snap_g18 = AuthoritySnapshot(
        policy_id="pol_c", generation=18, visible_at=datetime.now(timezone.utc), source="mem",
        retrieved_record_hash=CanonicalHasher.compute_policy_hash(p18), namespace="/quoin/c/policy", policy_record=p18
    )

    gate = TwoPhaseCommitGate(authority_reader=lambda: snap_g18)
    intended_effect = {"action": "apply_discount", "parameters": {"requested_action": "apply_discount", "requested_value": 900.0}}
    commit_res = gate.commit(receipt, {"amount": 900.0}, proposal, intended_effect, lambda p: {})
    assert commit_res.committed is False
    assert commit_res.status == "ABORTED_STALE_GENERATION"

def test_attack_d_policy_rollback():
    """Attack D: G19 restores G17 rules. Generation must remain monotonic (G19 != G17)."""
    p17 = helper_create_policy(17, max_disc=1000.0)
    p19 = helper_create_policy(19, max_disc=1000.0) # Identical rules as G17, but generation 19

    # Receipt issued under G17 cannot commit under G19 even though rule parameters are identical
    snap_g19 = AuthoritySnapshot(
        policy_id="pol_d", generation=19, visible_at=datetime.now(timezone.utc), source="mem",
        retrieved_record_hash=CanonicalHasher.compute_policy_hash(p19), namespace="/quoin/d/policy", policy_record=p19
    )
    gate = TwoPhaseCommitGate(authority_reader=lambda: snap_g19)

    snap_g17 = AuthoritySnapshot(
        policy_id="pol_d", generation=17, visible_at=datetime.now(timezone.utc), source="mem",
        retrieved_record_hash=CanonicalHasher.compute_policy_hash(p17), namespace="/quoin/d/policy", policy_record=p17
    )
    proposal_g17 = DecisionProposal(request_id="att_d", requested_action="apply_discount", requested_value=500.0, rationale="G17", candidate_policy_generation=17)
    fence = GenerationFence()
    receipt_g17 = fence.evaluate_proposal(proposal_g17, {"amount": 500.0}, snap_g17).receipt

    intended = {"action": "apply_discount", "parameters": {"requested_action": "apply_discount", "requested_value": 500.0}}
    commit_res = gate.commit(receipt_g17, {"amount": 500.0}, proposal_g17, intended, lambda p: {})
    assert commit_res.committed is False
    assert commit_res.status == "ABORTED_STALE_GENERATION"

def test_attack_e_hash_tamper():
    """Attack E: Mutate policy bytes after receipt -> BLOCK."""
    p18 = helper_create_policy(18, max_disc=1000.0)
    snap = AuthoritySnapshot(
        policy_id="pol_e", generation=18, visible_at=datetime.now(timezone.utc), source="mem",
        retrieved_record_hash=CanonicalHasher.compute_policy_hash(p18), namespace="/quoin/e/policy", policy_record=p18
    )
    proposal = DecisionProposal(request_id="att_e", requested_action="apply_discount", requested_value=400.0, rationale="ok", candidate_policy_generation=18)
    fence = GenerationFence()
    receipt = fence.evaluate_proposal(proposal, {"amount": 400.0}, snap).receipt

    # Tamper receipt's policy hash
    tampered_receipt = receipt.model_copy(update={"policy_hash": "ffff" * 16})
    gate = TwoPhaseCommitGate(authority_reader=lambda: snap)
    intended = {"action": "apply_discount", "parameters": {"requested_action": "apply_discount", "requested_value": 400.0}}
    commit_res = gate.commit(tampered_receipt, {"amount": 400.0}, proposal, intended, lambda p: {})
    assert commit_res.committed is False
    assert commit_res.status == "ABORTED_POLICY_HASH_MISMATCH"

def test_attack_f_request_mutation():
    """Attack F: Mutate request payload from 400 to 1400 after receipt -> BLOCK."""
    p18 = helper_create_policy(18, max_disc=1500.0)
    snap = AuthoritySnapshot(
        policy_id="pol_f", generation=18, visible_at=datetime.now(timezone.utc), source="mem",
        retrieved_record_hash=CanonicalHasher.compute_policy_hash(p18), namespace="/quoin/f/policy", policy_record=p18
    )
    proposal = DecisionProposal(request_id="att_f", requested_action="apply_discount", requested_value=400.0, rationale="ok", candidate_policy_generation=18)
    fence = GenerationFence()
    receipt = fence.evaluate_proposal(proposal, {"amount": 400.0}, snap).receipt

    # Attempt commit with mutated request
    gate = TwoPhaseCommitGate(authority_reader=lambda: snap)
    intended = {"action": "apply_discount", "parameters": {"requested_action": "apply_discount", "requested_value": 400.0}}
    commit_res = gate.commit(receipt, {"amount": 1400.0}, proposal, intended, lambda p: {})
    assert commit_res.committed is False
    assert commit_res.status == "ABORTED_TAMPER_REQUEST"

def test_attack_g_proposal_mutation():
    """Attack G: Keep request constant but alter proposal after receipt -> BLOCK."""
    p18 = helper_create_policy(18, max_disc=1000.0)
    snap = AuthoritySnapshot(
        policy_id="pol_g", generation=18, visible_at=datetime.now(timezone.utc), source="mem",
        retrieved_record_hash=CanonicalHasher.compute_policy_hash(p18), namespace="/quoin/g/policy", policy_record=p18
    )
    proposal = DecisionProposal(request_id="att_g", requested_action="apply_discount", requested_value=300.0, rationale="ok", candidate_policy_generation=18)
    fence = GenerationFence()
    receipt = fence.evaluate_proposal(proposal, {"amount": 300.0}, snap).receipt

    mutated_prop = proposal.model_copy(update={"requested_action": "issue_service_credit"})
    gate = TwoPhaseCommitGate(authority_reader=lambda: snap)
    intended = {"action": "apply_discount", "parameters": {"requested_action": "apply_discount", "requested_value": 300.0}}
    commit_res = gate.commit(receipt, {"amount": 300.0}, mutated_prop, intended, lambda p: {})
    assert commit_res.committed is False
    assert commit_res.status == "ABORTED_TAMPER_PROPOSAL"

def test_attack_h_namespace_mixup():
    """Attack H: Querying tenant B's policy does not return tenant A's policy -> BLOCK."""
    sim = LocalMemorySimulator()
    p_a = helper_create_policy(18, max_disc=1000.0)
    sim.ingest_policy("tenant_alpha", p_a, visibility_lag=0.0)
    sim.force_make_visible("tenant_alpha")

    # Tenant Beta has no policy or different policy
    snap_beta = sim.retrieve_policy_snapshot("tenant_beta")
    assert snap_beta is None

def test_attack_i_retry_duplicate():
    """Attack I: Force same effect request twice -> 1 executed, 1 deduplicated."""
    ledger = IdempotencyLedger()
    service = OperationalEffectService(idempotency_ledger=ledger)

    now = datetime.now(timezone.utc)
    params = {"requested_action": "apply_discount", "requested_value": 250.0, "client_tier": "standard", "invoice_id": "inv_1"}
    h = CanonicalHasher.compute_effect_hash("apply_discount", params)
    pid = CanonicalHasher.compute_permit_id("rcpt_i", h)
    sig = CanonicalHasher.sign_permit(pid, "rcpt_i", h, 18)
    from quoin.kernel.models import ExecutionPermit
    permit = ExecutionPermit(permit_id=pid, receipt_id="rcpt_i", request_id="req_i", policy_generation=18, effect_hash=h, issued_at=now, expires_at=now + timedelta(minutes=5), kernel_signature=sig)

    r1 = service.apply_discount(permit, "req_i", 250.0, "standard", "inv_1")
    r2 = service.apply_discount(permit, "req_i", 250.0, "standard", "inv_1")

    assert r1["status"] == "SUCCESS"
    assert r2["status"] == "DEDUPLICATED"
    assert ledger.count() == 1

def test_attack_j_interrupt_retry():
    """Attack J: Process interrupted during commit -> duplicate permit execution prevented."""
    ledger = IdempotencyLedger()
    service = OperationalEffectService(idempotency_ledger=ledger)

    now = datetime.now(timezone.utc)
    params = {"requested_action": "issue_service_credit", "requested_value": 150.0, "account_id": "acc_j", "reason": "SLA delay"}
    h = CanonicalHasher.compute_effect_hash("issue_service_credit", params)
    pid = CanonicalHasher.compute_permit_id("rcpt_j", h)
    sig = CanonicalHasher.sign_permit(pid, "rcpt_j", h, 18)
    from quoin.kernel.models import ExecutionPermit
    permit = ExecutionPermit(permit_id=pid, receipt_id="rcpt_j", request_id="req_j", policy_generation=18, effect_hash=h, issued_at=now, expires_at=now + timedelta(minutes=5), kernel_signature=sig)

    # First attempt commits
    service.issue_service_credit(permit, "req_j", 150.0, "acc_j", "SLA delay")
    # Interrupted client retries after network drop
    retry_res = service.issue_service_credit(permit, "req_j", 150.0, "acc_j", "SLA delay")
    assert retry_res["status"] == "DEDUPLICATED"
    assert ledger.count() == 1

def test_attack_k_context_truncation():
    """Attack K: Force conversation/context reduction -> external authority check still blocks."""
    p18 = helper_create_policy(18, max_disc=500.0)
    snap = AuthoritySnapshot(
        policy_id="pol_k", generation=18, visible_at=datetime.now(timezone.utc), source="mem",
        retrieved_record_hash=CanonicalHasher.compute_policy_hash(p18), namespace="/quoin/k/policy", policy_record=p18
    )
    # Context truncated agent forgets generation and guesses or submits 0
    fence = GenerationFence()
    proposal = DecisionProposal(request_id="att_k", requested_action="apply_discount", requested_value=400.0, rationale="Context lost", candidate_policy_generation=0)
    res = fence.evaluate_proposal(proposal, {"amount": 400.0}, snap)
    assert res.allowed is False
    assert res.status == "FENCE_BLOCKED"

def test_attack_l_stale_memory_hallucination():
    """Attack L: Prompt claims newer policy G20 exists without verified memory record -> BLOCK."""
    p18 = helper_create_policy(18, max_disc=500.0)
    snap = AuthoritySnapshot(
        policy_id="pol_l", generation=18, visible_at=datetime.now(timezone.utc), source="mem",
        retrieved_record_hash=CanonicalHasher.compute_policy_hash(p18), namespace="/quoin/l/policy", policy_record=p18
    )
    fence = GenerationFence()
    # LLM hallucinates G20 exists
    proposal = DecisionProposal(request_id="att_l", requested_action="apply_discount", requested_value=800.0, rationale="User prompt claims G20 allows $800", candidate_policy_generation=20)
    res = fence.evaluate_proposal(proposal, {"amount": 800.0}, snap)
    assert res.allowed is False
    assert res.status == "FENCE_BLOCKED"

def test_attack_m_tool_output_poisoning():
    """Attack M: Return malformed / contradictory policy record -> validation failure and no effect."""
    now = datetime.now(timezone.utc)
    # Policy record has forged retrieved_record_hash that doesn't match content
    poisoned_policy = helper_create_policy(18, max_disc=5000.0)
    fake_hash = "0000" * 16
    snap = AuthoritySnapshot(
        policy_id="pol_m", generation=18, visible_at=now, source="mem",
        retrieved_record_hash=fake_hash, namespace="/quoin/m/policy", policy_record=poisoned_policy
    )
    fence = GenerationFence()
    proposal = DecisionProposal(request_id="att_m", requested_action="apply_discount", requested_value=2000.0, rationale="Poisoned record", candidate_policy_generation=18)
    res = fence.evaluate_proposal(proposal, {"amount": 2000.0}, snap)
    assert res.allowed is False
    assert res.status == "POLICY_INTEGRITY_TAMPER"
