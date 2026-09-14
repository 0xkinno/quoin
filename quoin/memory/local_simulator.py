"""Deterministic high-fidelity memory simulator for local reproduction mode."""

import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from ..kernel.models import PolicyRecord, AuthoritySnapshot
from ..kernel.hasher import CanonicalHasher
from .namespaces import MemoryNamespaceManager

class LocalMemorySimulator:
    """Simulates AgentCore Memory asynchronous processing lag and namespace isolation."""

    def __init__(self, default_visibility_lag_seconds: float = 0.35):
        self.default_lag = default_visibility_lag_seconds
        # tenant_id -> list of (PolicyRecord, visible_after_monotonic_time)
        self._tenants: Dict[str, List[Tuple[PolicyRecord, float]]] = {}
        self._history: Dict[str, List[PolicyRecord]] = {}

    def ingest_policy(
        self,
        tenant_id: str,
        policy: PolicyRecord,
        visibility_lag: Optional[float] = None,
    ) -> Tuple[bool, float]:
        """Submit a policy update. Returns (acknowledged, ack_latency_ms)."""
        t0 = time.perf_counter()
        lag = visibility_lag if visibility_lag is not None else self.default_lag
        visible_after = time.monotonic() + lag

        if tenant_id not in self._tenants:
            self._tenants[tenant_id] = []
            self._history[tenant_id] = []

        self._tenants[tenant_id].append((policy, visible_after))
        self._history[tenant_id].append(policy)

        # Simulation of fast API write acknowledgement
        time.sleep(0.005)
        ack_ms = (time.perf_counter() - t0) * 1000.0
        return True, ack_ms

    def retrieve_policy_snapshot(self, tenant_id: str) -> Optional[AuthoritySnapshot]:
        """Query active long-term policy records for tenant."""
        records = self._tenants.get(tenant_id, [])
        if not records:
            return None

        now_mono = time.monotonic()
        now_dt = datetime.now(timezone.utc)

        # Find the latest policy record whose visible_after is <= now
        visible_policy: Optional[PolicyRecord] = None
        for policy, visible_after in reversed(records):
            if now_mono >= visible_after:
                visible_policy = policy
                break

        # If nothing is visible yet (first ingestion in progress), return None
        if not visible_policy:
            # If there's an older record that was visible, return it
            return None

        policy_hash = CanonicalHasher.compute_policy_hash(visible_policy)
        namespace = MemoryNamespaceManager.policy_namespace(tenant_id)

        return AuthoritySnapshot(
            policy_id=visible_policy.policy_id,
            generation=visible_policy.generation,
            visible_at=now_dt,
            source="local_simulator",
            retrieved_record_hash=policy_hash,
            namespace=namespace,
            policy_record=visible_policy,
        )

    def force_make_visible(self, tenant_id: str) -> None:
        """Immediately advance all pending ingestions to visible state (for test setup)."""
        if tenant_id in self._tenants:
            self._tenants[tenant_id] = [
                (policy, time.monotonic() - 1.0)
                for policy, _ in self._tenants[tenant_id]
            ]

    def list_history(self, tenant_id: str) -> List[PolicyRecord]:
        return list(self._history.get(tenant_id, []))
