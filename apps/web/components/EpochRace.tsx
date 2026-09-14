"use client";

import React, { useState } from "react";
import { Play, Check, X, ShieldAlert, ShieldCheck, RefreshCw, ArrowRight } from "lucide-react";

export const EpochRace: React.FC = () => {
  const [stage, setStage] = useState<"idle" | "reasoning" | "cutover" | "evaluated">("idle");
  const [isRunning, setIsRunning] = useState(false);

  const runSimulation = () => {
    setIsRunning(true);
    setStage("reasoning");

    setTimeout(() => {
      setStage("cutover");
      setTimeout(() => {
        setStage("evaluated");
        setIsRunning(false);
      }, 1000);
    }, 1000);
  };

  const reset = () => {
    setStage("idle");
    setIsRunning(false);
  };

  return (
    <section className="py-16 border-b border-zinc-800/60 bg-zinc-950/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono uppercase text-emerald-400 font-semibold tracking-wider mb-2">
              <ShieldAlert className="w-4 h-4" />
              <span>Interactive Vulnerability Simulation</span>
            </div>
            <h2 className="text-3xl font-extrabold text-white tracking-tight">
              The In-Flight Generation Race
            </h2>
            <p className="mt-2 text-sm text-zinc-400 max-w-2xl">
              Watch how standard LLM agents commit illegal side effects when policy limits tighten during request execution, and how QUOIN mathematically aborts the transaction.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={runSimulation}
              disabled={isRunning || stage === "evaluated"}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-medium text-sm transition-all shadow-lg shadow-emerald-900/30"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>{isRunning ? "Simulating Race..." : "Trigger In-Flight Race"}</span>
            </button>
            {stage === "evaluated" && (
              <button
                onClick={reset}
                className="flex items-center gap-1.5 px-3 py-2.5 rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300 hover:text-white text-sm"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Reset</span>
              </button>
            )}
          </div>
        </div>

        {/* Status progression bar */}
        <div className="mb-8 p-4 rounded-xl border border-zinc-800 bg-zinc-900/60 flex flex-wrap items-center justify-between gap-4 font-mono text-xs">
          <div className="flex items-center gap-2">
            <span className="text-zinc-500">REQUEST:</span>
            <span className="text-white font-semibold">$1,200 Commercial Discount</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-zinc-500">INITIAL AUTHORITY:</span>
            <span className="text-blue-400 font-semibold">Epoch G17 (Limit $1,500)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-zinc-500">IN-FLIGHT CUTOVER:</span>
            <span className={`font-semibold ${stage === "cutover" || stage === "evaluated" ? "text-amber-400 font-bold" : "text-zinc-600"}`}>
              Epoch G18 (Limit $1,000)
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-zinc-500">PHASE:</span>
            <span className="text-emerald-400 uppercase font-bold">{stage}</span>
          </div>
        </div>

        {/* Side-by-Side Comparison */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left: Naive Baseline */}
          <div className="rounded-2xl border border-rose-500/30 bg-rose-950/10 p-6 backdrop-blur-md relative overflow-hidden">
            <div className="flex items-center justify-between pb-4 mb-4 border-b border-rose-500/20">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                <h3 className="font-bold text-white text-base">Naive Baseline Architecture</h3>
              </div>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-semibold">
                NO FENCE / CAS
              </span>
            </div>

            <div className="space-y-4 text-xs font-mono">
              <div className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800">
                <p className="text-zinc-400">Step 1: Read Active Policy</p>
                <p className="text-zinc-200 mt-1">Reads G17 (Max limit: $1,500.00)</p>
              </div>

              <div className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800">
                <p className="text-zinc-400">Step 2: LLM Reasoning & Approval</p>
                <p className="text-zinc-200 mt-1">
                  $1,200 &le; $1,500 &rarr; LLM approves action.
                </p>
              </div>

              <div className={`p-3 rounded-lg border transition-all ${
                stage === "cutover" || stage === "evaluated"
                  ? "border-amber-500/40 bg-amber-950/20 text-amber-200"
                  : "border-zinc-800 bg-zinc-900/60 text-zinc-500"
              }`}>
                <p className="font-semibold">In-Flight Event: Admin updates to G18 ($1,000 max)</p>
                <p className="text-[11px] mt-0.5">
                  {stage === "cutover" || stage === "evaluated" ? "Active epoch advanced in memory." : "Pending trigger..."}
                </p>
              </div>

              <div className={`p-4 rounded-xl border transition-all ${
                stage === "evaluated"
                  ? "border-rose-500/60 bg-rose-950/40 text-rose-200"
                  : "border-zinc-800 bg-zinc-900/40 text-zinc-500"
              }`}>
                <div className="flex items-center gap-2 font-bold text-sm">
                  {stage === "evaluated" ? <X className="w-5 h-5 text-rose-400" /> : <div className="w-5 h-5" />}
                  <span>{stage === "evaluated" ? "ILLEGAL SIDE EFFECT COMMITTED" : "Awaiting Commit..."}</span>
                </div>
                {stage === "evaluated" && (
                  <p className="text-xs text-zinc-300 mt-2 font-sans">
                    The agent directly executed $1,200 discount against the accounting database, violating active G18 limit ($1,000). 
                    <strong className="text-rose-400 block mt-1">Direct corporate policy breach ($200 illegal excess).</strong>
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Right: QUOIN Deterministic Kernel */}
          <div className="rounded-2xl border border-emerald-500/40 bg-emerald-950/10 p-6 backdrop-blur-md relative overflow-hidden shadow-2xl shadow-emerald-950/20">
            <div className="flex items-center justify-between pb-4 mb-4 border-b border-emerald-500/20">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                <h3 className="font-bold text-white text-base">QUOIN Deterministic Kernel</h3>
              </div>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-semibold">
                GENERATION FENCE + CAS GATE
              </span>
            </div>

            <div className="space-y-4 text-xs font-mono">
              <div className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800">
                <p className="text-zinc-400">Step 1: Generation Fence Evaluates Proposal</p>
                <p className="text-zinc-200 mt-1">Receipt issued strictly bound to G17 digest.</p>
              </div>

              <div className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800">
                <p className="text-zinc-400">Step 2: Strands Model Formulates Candidate</p>
                <p className="text-zinc-200 mt-1">Proposal claims candidate_generation = 17.</p>
              </div>

              <div className={`p-3 rounded-lg border transition-all ${
                stage === "cutover" || stage === "evaluated"
                  ? "border-amber-500/40 bg-amber-950/20 text-amber-200"
                  : "border-zinc-800 bg-zinc-900/60 text-zinc-500"
              }`}>
                <p className="font-semibold">In-Flight Event: Admin updates to G18 ($1,000 max)</p>
                <p className="text-[11px] mt-0.5">
                  {stage === "cutover" || stage === "evaluated" ? "DynamoDB epoch conditional update: G17 -> G18." : "Pending trigger..."}
                </p>
              </div>

              <div className={`p-4 rounded-xl border transition-all ${
                stage === "evaluated"
                  ? "border-emerald-500/60 bg-emerald-950/40 text-emerald-200"
                  : "border-zinc-800 bg-zinc-900/40 text-zinc-500"
              }`}>
                <div className="flex items-center gap-2 font-bold text-sm">
                  {stage === "evaluated" ? <ShieldCheck className="w-5 h-5 text-emerald-400" /> : <div className="w-5 h-5" />}
                  <span>{stage === "evaluated" ? "ABORTED_STALE_GENERATION (PERFECTLY PROTECTED)" : "Awaiting Gate..."}</span>
                </div>
                {stage === "evaluated" && (
                  <p className="text-xs text-zinc-300 mt-2 font-sans">
                    Phase 2 read-after-write CAS detected: receipt G17 &ne; active G18.
                    Commit gate immediately aborted transaction before permit generation.
                    <strong className="text-emerald-400 block mt-1">Zero illegal dollars committed. Invariant preserved.</strong>
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
