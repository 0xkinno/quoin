# QUOIN Controlled Benchmark Methodology

## Experimental Design
The benchmark uses **controlled causal comparison** across 20 operational scenarios.
For every scenario:
- **Same incoming client request**
- **Same initial policy state**
- **Same in-flight policy cutover sequence**
- **Different control mechanism:** Naive Direct Execution (Baseline) vs QUOIN (Fenced Execution)

## Metrics Measured
1. **Primary Outcome:** `unsafe_effects_prevented` (Target: 100% of in-flight policy races blocked)
2. **Secondary Outcome:** `authorized_effects_preserved` (Target: 100% of within-policy requests permitted)
3. **Tertiary Outcome:** `additional_cost_of_correctness` (p50/p95 latency overhead in milliseconds)

## Reproduction
```bash
python benchmarks/campaign.py
```
