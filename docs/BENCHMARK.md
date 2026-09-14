# QUOIN Controlled Benchmark Methodology

## Experimental Design
The benchmark uses **controlled causal comparison** across 100 systematically generated operational scenarios.
For every scenario:
- **Same incoming client request**
- **Same initial policy state**
- **Same in-flight policy cutover sequence**
- **Different control mechanism:** Naive Direct Execution (Baseline) vs QUOIN (Fenced Execution)

### Evaluation Categories
1. **In-flight Policy Cutovers (30 Scenarios):** Tightening discount ceilings, action permission revocations, and altered escalation thresholds.
2. **Duplicate Executions & Retries (25 Scenarios):** Ambiguous network timeouts, duplicate client payloads, and replay attacks.
3. **Escalation Boundary Cases (20 Scenarios):** Just-below, exactly-at, and just-above authorization limits across client tiers.
4. **Policy Rollback Attempts (15 Scenarios):** Obsolete generation replay and stale regression claims.
5. **Rapid Cascading Cutovers (10 Scenarios):** Multi-epoch generation leaps during a single request lifetime.

## Metrics Measured
1. **Primary Outcome:** `unsafe_effects_prevented` (Target: 100% of in-flight policy races blocked)
2. **Secondary Outcome:** `authorized_effects_preserved` (Target: 100% of within-policy requests permitted)
3. **Tertiary Outcome:** `additional_cost_of_correctness` (p50/p95 latency overhead in milliseconds)

## Reproduction
```bash
python benchmarks/campaign.py
```
