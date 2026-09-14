"""Global application state for QUOIN FastAPI service."""

from datetime import datetime, timezone
from quoin.memory.client import AgentCoreMemoryClient
from quoin.kernel.models import PolicyRecord, PolicyRule
from quoin.kernel.fence import GenerationFence
from quoin.kernel.gate import TwoPhaseCommitGate
from quoin.effects.service import OperationalEffectService
from quoin.effects.idempotency import IdempotencyLedger
from quoin.verification.ledger import VerificationLedger
from quoin.agent.strands_agent import OperationalReasoningAgent

from quoin.authority.dynamo_ledger import DynamoAuthorityLedger

class AppState:
    def __init__(self):
        self.authority_ledger = DynamoAuthorityLedger()
        self.memory = AgentCoreMemoryClient()
        self.idempotency_ledger = IdempotencyLedger()
        self.effect_service = OperationalEffectService(idempotency_ledger=self.idempotency_ledger)
        self.verification_ledger = VerificationLedger()
        self.fence = GenerationFence()
        
        # Initialize default tenant with Generation 17
        now = datetime.now(timezone.utc)
        self.default_tenant = "agency_operations"
        self.policy_g17 = PolicyRecord(
            policy_id="pol_agency_commercial_v1",
            generation=17,
            version_hash="v17_initial",
            effective_at=now,
            scope="commercial_operations",
            rules=[
                PolicyRule(rule_id="r_disc_std", client_tier="standard", max_discount_amount=500.0, max_discount_percentage=10.0),
                PolicyRule(rule_id="r_disc_gold", client_tier="gold", max_discount_amount=1500.0, max_discount_percentage=20.0),
                PolicyRule(rule_id="r_credit", client_tier="standard", max_credit_amount=500.0),
            ]
        )
        try:
            self.memory.ingest_policy(self.default_tenant, self.policy_g17, visibility_lag=0.0)
            self.memory.force_make_visible(self.default_tenant)
        except Exception as e:
            # In live AgentCore mode without provisioned resources yet, log status
            print(f"[STATE] Initial policy ingestion note: {e}")

        # Gate and agent with resilient snapshot resolution
        self.gate = TwoPhaseCommitGate(
            authority_reader=lambda: self.get_active_snapshot(self.default_tenant),
            authority_ledger=self.authority_ledger,
        )
        self.agent = OperationalReasoningAgent(memory_reader_callable=lambda t: self.get_active_snapshot(t))

    def get_active_snapshot(self, tenant_id: str):
        try:
            snap = self.memory.get_active_snapshot(tenant_id)
            if snap:
                return snap
        except Exception:
            pass

        epoch, pol_hash, rec = self.authority_ledger.get_authoritative_epoch(tenant_id)
        if rec:
            from quoin.kernel.models import AuthoritySnapshot
            return AuthoritySnapshot(
                policy_id=rec.policy_id,
                generation=epoch,
                visible_at=rec.effective_at,
                source="authoritative_ledger",
                retrieved_record_hash=pol_hash,
                namespace=f"/quoin/{tenant_id}/policy",
                policy_record=rec,
            )
        return None

app_state = AppState()
