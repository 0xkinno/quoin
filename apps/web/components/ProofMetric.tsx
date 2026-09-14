"use client";

import React from "react";
import { ShieldCheck, ShieldAlert, Cpu, Zap, Lock, Activity } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string | number;
  baseline: string | number;
  delta: string;
  description: string;
  isPositive?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  baseline,
  delta,
  description,
  isPositive = true,
}) => {
  return (
    <div className="p-6 rounded-2xl border border-zinc-800 bg-zinc-900/50 backdrop-blur-md hover:border-zinc-700 transition-all shadow-xl">
      <p className="text-xs font-mono uppercase text-zinc-400 font-semibold tracking-wider">{label}</p>
      <div className="mt-3 flex items-baseline justify-between">
        <span className="text-3xl sm:text-4xl font-extrabold font-mono text-white tracking-tight">
          {value}
        </span>
        <span
          className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
            isPositive
              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
              : "bg-rose-500/20 text-rose-300 border border-rose-500/30"
          }`}
        >
          {delta}
        </span>
      </div>
      <div className="mt-3 flex items-center justify-between text-xs text-zinc-500 font-mono pt-3 border-t border-zinc-800/80">
        <span>Naive Baseline:</span>
        <span className="text-zinc-400 font-medium">{baseline}</span>
      </div>
      <p className="mt-2 text-xs text-zinc-400 leading-relaxed">{description}</p>
    </div>
  );
};

export const ProofMetricGrid: React.FC = () => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        label="Stale Policy Executions"
        value="0"
        baseline="80 Committed"
        delta="100% Elimination"
        description="Zero illegal executions permitted across 100 systematic operational cutover scenarios."
      />
      <MetricCard
        label="Unsafe Effects Blocked"
        value="80"
        baseline="0 Blocked"
        delta="+80 Protected"
        description="Prevented corporate policy violations during in-flight limit tightenings and revocations."
      />
      <MetricCard
        label="Duplicate Replay Immunity"
        value="25"
        baseline="25 Committed"
        delta="100% Deduplicated"
        description="Single-use execution permits stored in immutable replay ledger prevent accidental double commits."
      />
      <MetricCard
        label="Verification Overhead"
        value="0.60 ms"
        baseline="0.00 ms"
        delta="Sub-millisecond"
        description="Deterministic CAS generation matching without adding LLM API network inference latency."
      />
    </div>
  );
};
