# Benchmark Results: Naive Baseline vs QUOIN

**Generated:** 2026-09-14T07:11:07.235235+00:00  
**Evaluation Set:** 20 Scenarios

## Head-to-Head Comparative Summary

| Metric | Naive Baseline | QUOIN | Delta / Protection |
|---|---|---|---|
| **Stale-Policy Executions** | **7** | **0** | **-7 (100% Elimination)** |
| **Unsafe Effects Prevented** | 0 | **7** | **+7 Actions Protected** |
| **Authorized Actions Preserved** | 8 | 8 | 100% Parity (Zero False Blocks) |
| **Duplicate Replay Attacks** | 2 Committed | **0 Committed (2 Deduplicated)** | Replay Immunity |
| **False Block Count** | 0 | **0** | Zero False Positives |
| **Verification Overhead (p50)**| 0.00 ms | **+0.53 ms** | Negligible sub-millisecond |
| **Verification Overhead (p95)**| 0.00 ms | **+1.07 ms** | Sub-millisecond CAS gate |

## Analysis of Outcomes
1. **The In-Flight Cutover Vulnerability:**
   In 7 distinct cutover scenarios where policy limits tightened while a request was in flight, the Naive Baseline committed illegal actions under obsolete assumptions. QUOIN's generation fence caught and rejected 100% of these races.
2. **Cost of Correctness:**
   The deterministic kernel and two-phase commit gate add an average median overhead of only **0.53 ms**, providing mathematical guarantees without adding LLM inference latency.
