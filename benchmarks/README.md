# QUOIN Controlled Benchmark Suite

This directory contains the controlled causal benchmark comparing standard un-fenced agent execution (Naive Baseline) against QUOIN across 20 operational scenarios.

## Execution
```bash
python benchmarks/campaign.py
```

## Structure
- `scenarios.json`: 20 controlled scenarios with defined in-flight cutover events.
- `baseline/naive_agent.py`: Naive agent committing without a generation fence.
- `quoin_runner/fenced_runner.py`: QUOIN agent with two-phase commit gate and generation fence.
- `campaign.py`: Automated runner producing `results.json`.
- `results.json`: Generated benchmark metrics.
