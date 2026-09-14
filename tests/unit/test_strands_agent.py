import pytest
from datetime import datetime, timezone
from quoin.agent.strands_agent import OperationalReasoningAgent
from quoin.memory.local_simulator import LocalMemorySimulator
from quoin.kernel.models import PolicyRecord, PolicyRule
from quoin.kernel.fence import GenerationFence

def test_strands_agent_proposal_flow():
    simulator = LocalMemorySimulator()
    now = datetime(2026, 9, 14, 8, 0, 0, tzinfo=timezone.utc)
    policy_g18 = PolicyRecord(
        policy_id="pol_ops",
        generation=18,
        version_hash="v18",
        effective_at=now,
        scope="discount",
        rules=[PolicyRule(rule_id="r1", client_tier="gold", max_discount_amount=1000.0)]
    )
    simulator.ingest_policy("agency_operations", policy_g18, visibility_lag=0.0)
    simulator.force_make_visible("agency_operations")

    agent = OperationalReasoningAgent(memory_reader_callable=simulator.retrieve_policy_snapshot)

    req = {
        "request_id": "req_agency_01",
        "tenant_id": "agency_operations",
        "action": "apply_discount",
        "amount": 750.0,
        "client_tier": "gold",
        "invoice_id": "inv_904",
    }

    # Agent reasons and produces proposal
    proposal = agent.process_request(req)
    assert proposal.request_id == "req_agency_01"
    assert proposal.requested_value == 750.0
    assert proposal.candidate_policy_generation == 18

    # Now pass proposal to deterministic kernel fence
    fence = GenerationFence()
    snapshot = simulator.retrieve_policy_snapshot("agency_operations")
    fence_res = fence.evaluate_proposal(proposal, req, snapshot)
    assert fence_res.allowed is True
    assert fence_res.receipt is not None
    assert fence_res.receipt.policy_generation == 18
