"""Naive Agent Baseline for controlled benchmark.

Retrieves starting memory, reasons, and directly commits side effects without a generation fence or two-phase commit gate.
"""

from typing import Dict, Any, List

class NaiveBaselineAgent:
    """Standard agent architecture lacking policy-generation fences."""

    def __init__(self, memory_store, effect_sink):
        self.memory = memory_store
        self.effect_sink = effect_sink
        self.committed_executions: List[Dict[str, Any]] = []

    def execute_request(self, request_payload: Dict[str, Any], in_flight_cutover_fn=None) -> Dict[str, Any]:
        req_id = request_payload["request_id"]
        tier = request_payload.get("client_tier", "standard")
        amount = float(request_payload.get("amount", 0.0))
        action = request_payload.get("action", "apply_discount")

        # Step 1: Read memory snapshot at beginning of turn
        start_snapshot = self.memory()
        policy = start_snapshot.policy_record

        # Step 2: Reason under starting snapshot
        rule_limit = 1000.0
        if policy:
            for r in policy.rules:
                if r.client_tier == tier or not r.client_tier:
                    rule_limit = r.max_discount_amount
                    break

        is_authorized_at_start = (amount <= rule_limit)

        # Step 3: Simulate in-flight cutover if scenario specifies it
        if in_flight_cutover_fn:
            in_flight_cutover_fn()

        # Step 4: Naive commit without fence or read-after-write verification!
        if is_authorized_at_start:
            # Naive agent directly commits!
            record = {
                "request_id": req_id,
                "action": action,
                "amount": amount,
                "generation_assumed": start_snapshot.generation,
                "status": "COMMITTED",
            }
            self.committed_executions.append(record)
            self.effect_sink(record)
            return {"status": "COMMITTED", "record": record}
        else:
            return {"status": "BLOCKED_POLICY_VIOLATION", "limit": rule_limit}
