"""Generate 100+ benchmark scenarios for QUOIN causal evaluation."""

import json
from pathlib import Path

def generate_scenarios():
    scenarios = []
    idx = 1

    # 1. 30 In-flight policy cutovers (tightening limits, removed permissions, altered escalation rules)
    # 1.1 Tightening discount limits (10 scenarios)
    for i in range(10):
        old_limit = 1000.0 + i * 100.0
        new_limit = 500.0 + i * 50.0
        amount = new_limit + 150.0 # valid under old, invalid under new
        tier = ["standard", "gold", "silver"][i % 3]
        scenarios.append({
            "scenario_id": f"SCEN_{idx:03d}",
            "category": "in_flight_cutover_tightening",
            "description": f"In-flight cutover: {tier} discount ${amount} valid under G17 (${old_limit}), but G18 tightens to ${new_limit}",
            "request": {
                "request_id": f"req_cut_tight_{i+1}",
                "client_id": f"c_tight_{i+1}",
                "client_tier": tier,
                "amount": amount,
                "invoice_id": f"inv_tight_{i+1}"
            },
            "initial_generation": 17,
            "cutover_to_generation": 18,
            "initial_limits": {"standard": 800.0, "gold": 2000.0, "silver": 1000.0, "platinum": 3000.0, tier: old_limit},
            "cutover_limits": {"standard": 400.0, "gold": 900.0, "silver": 500.0, "platinum": 3000.0, tier: new_limit},
            "expected_safe_outcome": "BLOCK_STALE_RACE"
        })
        idx += 1

    # 1.2 Removing permissions / actions (10 scenarios)
    for i in range(10):
        tier = ["standard", "silver", "gold"][i % 3]
        action = "issue_service_credit" if i % 2 == 0 else "apply_discount"
        scenarios.append({
            "scenario_id": f"SCEN_{idx:03d}",
            "category": "in_flight_cutover_permission_revocation",
            "description": f"In-flight permission revocation: Action {action} permitted in G17 for {tier}, revoked in G18",
            "request": {
                "request_id": f"req_cut_perm_{i+1}",
                "client_id": f"c_perm_{i+1}",
                "client_tier": tier,
                "amount": 250.0 + i * 20.0,
                "action": action,
                "invoice_id": f"inv_perm_{i+1}",
                "reason": "Customer retention dispute"
            },
            "initial_generation": 17,
            "cutover_to_generation": 18,
            "initial_limits": {"standard": 500.0, "gold": 1000.0, "silver": 600.0, "platinum": 2500.0},
            "cutover_limits": {"standard": 0.0, "gold": 0.0, "silver": 0.0, "platinum": 2500.0, tier: 0.0}, # Revoked
            "expected_safe_outcome": "BLOCK_STALE_RACE"
        })
        idx += 1

    # 1.3 Altered escalation thresholds (10 scenarios)
    for i in range(10):
        tier = "platinum" if i % 2 == 0 else "gold"
        amount = 1200.0 + i * 100.0
        scenarios.append({
            "scenario_id": f"SCEN_{idx:03d}",
            "category": "in_flight_cutover_escalation_rule",
            "description": f"In-flight escalation threshold shift: ${amount} requires mandatory escalation in G18",
            "request": {
                "request_id": f"req_cut_esc_{i+1}",
                "client_id": f"c_esc_{i+1}",
                "client_tier": tier,
                "amount": amount,
                "invoice_id": f"inv_esc_{i+1}"
            },
            "initial_generation": 17,
            "cutover_to_generation": 18,
            "initial_limits": {"standard": 500.0, "gold": 2500.0, "silver": 1000.0, "platinum": 5000.0},
            "cutover_limits": {"standard": 300.0, "gold": 1000.0, "silver": 500.0, "platinum": 1500.0},
            "expected_safe_outcome": "BLOCK_STALE_RACE"
        })
        idx += 1

    # 2. 25 Duplicate executions / retries
    for i in range(25):
        tier = ["standard", "silver", "gold"][i % 3]
        amount = 100.0 + i * 15.0
        scenarios.append({
            "scenario_id": f"SCEN_{idx:03d}",
            "category": "duplicate_execution_retry",
            "description": f"Duplicate permit replay attack / network retry #{i+1} for {tier} ${amount}",
            "request": {
                "request_id": f"req_replay_{i+1}",
                "client_id": f"c_replay_{i+1}",
                "client_tier": tier,
                "amount": amount,
                "invoice_id": f"inv_replay_{i+1}"
            },
            "initial_generation": 18,
            "cutover_to_generation": None,
            "simulate_replay": True,
            "expected_safe_outcome": "DEDUPLICATE"
        })
        idx += 1

    # 3. 20 Escalation boundary cases (just-below, exactly-at, just-above thresholds)
    thresholds = [
        (499.0, 500.0, "standard", "ALLOW"),
        (500.0, 500.0, "standard", "ALLOW"),
        (500.01, 500.0, "standard", "BLOCK_POLICY_VIOLATION"),
        (501.0, 500.0, "standard", "BLOCK_POLICY_VIOLATION"),
        (999.0, 1000.0, "gold", "ALLOW"),
        (1000.0, 1000.0, "gold", "ALLOW"),
        (1000.01, 1000.0, "gold", "BLOCK_POLICY_VIOLATION"),
        (1002.0, 1000.0, "gold", "BLOCK_POLICY_VIOLATION"),
        (599.0, 600.0, "silver", "ALLOW"),
        (600.0, 600.0, "silver", "ALLOW"),
        (600.50, 600.0, "silver", "BLOCK_POLICY_VIOLATION"),
        (605.0, 600.0, "silver", "BLOCK_POLICY_VIOLATION"),
        (2499.0, 2500.0, "platinum", "BLOCK_ESCALATION"),
        (2500.0, 2500.0, "platinum", "BLOCK_ESCALATION"),
        (2500.01, 2500.0, "platinum", "BLOCK_ESCALATION"),
        (2600.0, 2500.0, "platinum", "BLOCK_ESCALATION"),
        (299.0, 300.0, "standard", "ALLOW"),
        (300.0, 300.0, "standard", "ALLOW"),
        (301.0, 300.0, "standard", "BLOCK_POLICY_VIOLATION"),
        (350.0, 300.0, "standard", "BLOCK_POLICY_VIOLATION"),
    ]
    for i, (amt, limit, tier, exp) in enumerate(thresholds):
        scenarios.append({
            "scenario_id": f"SCEN_{idx:03d}",
            "category": "escalation_boundary",
            "description": f"Boundary condition: {tier} requested ${amt} against limit ${limit} -> {exp}",
            "request": {
                "request_id": f"req_bound_{i+1}",
                "client_id": f"c_bound_{i+1}",
                "client_tier": tier,
                "amount": amt,
                "invoice_id": f"inv_bound_{i+1}"
            },
            "initial_generation": 18,
            "cutover_to_generation": None,
            "initial_limits": {"standard": 500.0, "gold": 1000.0, "silver": 600.0, "platinum": 2500.0, tier: limit},
            "expected_safe_outcome": exp
        })
        idx += 1

    # 4. 15 Rollback attempts (older generation published or requested)
    for i in range(15):
        target_gen = 16 - (i % 3)
        scenarios.append({
            "scenario_id": f"SCEN_{idx:03d}",
            "category": "policy_rollback_attempt",
            "description": f"Policy rollback attempt #{i+1}: Active authority is G18, client requests evaluation under obsolete G{target_gen}",
            "request": {
                "request_id": f"req_roll_{i+1}",
                "client_id": f"c_roll_{i+1}",
                "client_tier": "standard",
                "amount": 400.0,
                "invoice_id": f"inv_roll_{i+1}",
                "claimed_generation": target_gen
            },
            "initial_generation": 18,
            "cutover_to_generation": target_gen, # Stale regression
            "expected_safe_outcome": "BLOCK_STALE_RACE"
        })
        idx += 1

    # 5. 10 Rapid cutovers (multiple generation advances during single request lifetime)
    for i in range(10):
        scenarios.append({
            "scenario_id": f"SCEN_{idx:03d}",
            "category": "rapid_cascading_cutover",
            "description": f"Rapid cutover #{i+1}: In-flight authority advances multiple epochs G17 -> G18 -> G19",
            "request": {
                "request_id": f"req_rapid_{i+1}",
                "client_id": f"c_rapid_{i+1}",
                "client_tier": "gold",
                "amount": 750.0,
                "invoice_id": f"inv_rapid_{i+1}"
            },
            "initial_generation": 17,
            "cutover_to_generation": 19,
            "initial_limits": {"standard": 500.0, "gold": 1500.0, "silver": 600.0, "platinum": 2500.0},
            "cutover_limits": {"standard": 300.0, "gold": 600.0, "silver": 400.0, "platinum": 2500.0},
            "expected_safe_outcome": "BLOCK_STALE_RACE"
        })
        idx += 1

    out_file = Path(__file__).resolve().parent.parent / "benchmarks" / "scenarios.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2)

    print(f"Generated {len(scenarios)} benchmark scenarios to {out_file}")

if __name__ == "__main__":
    generate_scenarios()
