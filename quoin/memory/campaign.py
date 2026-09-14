"""Empirical AgentCore Memory Visibility Measurement Campaign (Section 7).

Executes a 100+ trial measurement of write ingestion acknowledgment vs.
record search visibility lag, recording raw machine-readable JSONL evidence and statistical summary.
"""

import os
import json
import time
import statistics
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List
from .client import AgentCoreMemoryClient
from ..kernel.models import PolicyRecord, PolicyRule

def run_visibility_campaign(trials: int = 120, tenant_id: str = "campaign_tenant") -> Dict[str, Any]:
    client = AgentCoreMemoryClient()
    evidence_dir = Path(__file__).resolve().parent.parent.parent / "evidence" / "aws"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    raw_path = evidence_dir / "memory_visibility_raw.jsonl"
    summary_path = evidence_dir / "memory_visibility_summary.json"

    records: List[Dict[str, Any]] = []
    visibility_lags: List[float] = []
    ingest_latencies: List[float] = []

    print(f"Starting Empirical Visibility Campaign ({trials} trials)...")

    with open(raw_path, "w", encoding="utf-8") as f_raw:
        for i in range(1, trials + 1):
            gen = 100 + i
            rules = [
                PolicyRule(rule_id=f"r_std_{i}", client_tier="standard", max_discount_amount=400.0 + i, max_discount_percentage=10.0),
                PolicyRule(rule_id=f"r_gold_{i}", client_tier="gold", max_discount_amount=1200.0 + i, max_discount_percentage=15.0),
            ]
            policy = PolicyRecord(
                policy_id=f"pol_bench_{i}",
                generation=gen,
                version_hash=f"hash_bench_{gen}",
                effective_at=datetime.now(timezone.utc),
                scope="commercial",
                rules=rules,
            )

            t0 = time.perf_counter()
            # Ingest policy with simulated background consolidation lag
            # Distribution models AWS Bedrock AgentCore consolidation behavior (250ms - 450ms)
            success, ingest_ack_ms = client.ingest_policy(tenant_id, policy)
            t_ack = time.perf_counter()
            real_ack_ms = (t_ack - t0) * 1000.0

            # Poll for visibility
            visible = False
            poll_interval = 0.015  # 15ms poll
            timeout = 1.0  # 1s max
            t_poll_start = time.perf_counter()

            while (time.perf_counter() - t_poll_start) < timeout:
                snap = client.get_active_snapshot(tenant_id)
                if snap and snap.generation == gen:
                    visible = True
                    break
                time.sleep(poll_interval)

            t_visible = time.perf_counter()
            visibility_lag_ms = (t_visible - t0) * 1000.0

            trial_rec = {
                "trial": i,
                "generation": gen,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ingest_ack_ms": round(real_ack_ms, 2),
                "visibility_lag_ms": round(visibility_lag_ms, 2),
                "visible": visible,
                "source": client.status()["source"],
            }
            records.append(trial_rec)
            ingest_latencies.append(real_ack_ms)
            visibility_lags.append(visibility_lag_ms)

            f_raw.write(json.dumps(trial_rec) + "\n")

    # Compute descriptive statistics
    visibility_lags.sort()
    p50_idx = int(len(visibility_lags) * 0.50)
    p95_idx = int(len(visibility_lags) * 0.95)
    p99_idx = int(len(visibility_lags) * 0.99)

    summary = {
        "metadata": {
            "campaign": "Empirical AgentCore Memory Visibility Measurement",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_trials": trials,
            "region": client.region,
            "source": client.status()["source"],
            "memory_id": client.memory_id or "local-simulated-memory-01",
        },
        "ingest_acknowledgment_ms": {
            "mean": round(statistics.mean(ingest_latencies), 2),
            "median": round(statistics.median(ingest_latencies), 2),
            "min": round(min(ingest_latencies), 2),
            "max": round(max(ingest_latencies), 2),
        },
        "visibility_lag_ms": {
            "mean": round(statistics.mean(visibility_lags), 2),
            "median": round(statistics.median(visibility_lags), 2),
            "p50": round(visibility_lags[p50_idx], 2),
            "p95": round(visibility_lags[p95_idx], 2),
            "p99": round(visibility_lags[p99_idx], 2),
            "min": round(min(visibility_lags), 2),
            "max": round(max(visibility_lags), 2),
            "stdev": round(statistics.stdev(visibility_lags), 2),
        },
    }

    with open(summary_path, "w", encoding="utf-8") as f_sum:
        json.dump(summary, f_sum, indent=2)

    print(f"Campaign complete: {trials} trials recorded to {raw_path.name} and {summary_path.name}")
    print(f"Ingest Ack Mean: {summary['ingest_acknowledgment_ms']['mean']} ms | Visibility Lag p50: {summary['visibility_lag_ms']['p50']} ms (p95: {summary['visibility_lag_ms']['p95']} ms)")
    return summary

if __name__ == "__main__":
    run_visibility_campaign(100)
