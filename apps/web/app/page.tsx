"use client";

import Link from "next/link";
import { useState } from "react";
import { Shield, ArrowRight, CheckCircle, AlertTriangle, Play, RefreshCw, Lock, Zap, FileText } from "lucide-react";

export default function LandingPage() {
  const [interactiveRace, setInteractiveRace] = useState<"IDLE" | "RACE_OCCURRED" | "BLOCKED">("IDLE");

  return (
    <div className="space-y-24 pb-24">
      {/* 1. HERO SECTION */}
      <section className="pt-20 pb-12 border-b border-paper-200">
        <div className="max-w-5xl mx-auto px-6 text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-paper-100 border border-paper-200 text-xs font-mono text-graphite-muted">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
            AWS Agents for Humans 2026 &middot; Professional Agents Track
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-graphite-main leading-[1.08]">
            Accepted is not the same as visible.
          </h1>

          <p className="text-lg md:text-xl text-graphite-muted max-w-3xl mx-auto font-normal leading-relaxed">
            QUOIN prevents professional agents from acting on stale policy by fencing every consequential action to the exact policy generation the agent has actually verified as visible.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              href="/console"
              className="px-6 py-3.5 rounded-lg bg-graphite-main hover:bg-black text-white font-medium text-sm flex items-center gap-2 transition-all shadow-sm"
            >
              Launch Cutover Console <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/lab"
              className="px-6 py-3.5 rounded-lg bg-white hover:bg-paper-50 text-graphite-main border border-paper-200 font-medium text-sm transition-all"
            >
              Open Break It Lab (13 Attacks)
            </Link>
          </div>

          {/* Core Metrics Ribbon */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-12 text-left">
            <div className="p-4 rounded-xl bg-white border border-paper-200 shadow-sm">
              <div className="text-2xl font-bold font-mono text-graphite-main">0</div>
              <div className="text-xs text-graphite-muted mt-1">Stale Executions Allowed</div>
            </div>
            <div className="p-4 rounded-xl bg-white border border-paper-200 shadow-sm">
              <div className="text-2xl font-bold font-mono text-emerald-600">13 / 13</div>
              <div className="text-xs text-graphite-muted mt-1">Attacks Neutralized</div>
            </div>
            <div className="p-4 rounded-xl bg-white border border-paper-200 shadow-sm">
              <div className="text-2xl font-bold font-mono text-blue-600">321.6 ms</div>
              <div className="text-xs text-graphite-muted mt-1">AgentCore Visibility Gap (p50)</div>
            </div>
            <div className="p-4 rounded-xl bg-white border border-paper-200 shadow-sm">
              <div className="text-2xl font-bold font-mono text-graphite-main">+0.53 ms</div>
              <div className="text-xs text-graphite-muted mt-1">Verification Overhead (p50)</div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. THE FAILURE IN ONE SENTENCE */}
      <section className="max-w-5xl mx-auto px-6">
        <div className="p-8 rounded-2xl bg-paper-100 border border-paper-200 space-y-4">
          <div className="text-xs font-mono uppercase tracking-widest text-rose-600 font-semibold">The Operational Failure</div>
          <h2 className="text-2xl md:text-3xl font-bold text-graphite-main tracking-tight">
            Policies change while agents are still running.
          </h2>
          <p className="text-graphite-muted leading-relaxed">
            In professional operations, policies (discounts, refunds, scope expansions) change dynamically. When a policy update is submitted to AWS AgentCore Memory, the API confirms ingestion immediately, but the resulting long-term memory records become available only after background consolidation. If an in-flight agent acts during this window, it approves actions that are illegal under the new policy.
          </p>
        </div>
      </section>

      {/* 3. INTERACTIVE CUTOVER RACE SIMULATOR */}
      <section className="max-w-5xl mx-auto px-6 space-y-8">
        <div className="text-center space-y-2">
          <div className="text-xs font-mono uppercase tracking-widest text-blue-600 font-semibold">Interactive Demonstration</div>
          <h2 className="text-3xl font-bold tracking-tight text-graphite-main">The Live In-Flight Policy Race</h2>
          <p className="text-sm text-graphite-muted max-w-xl mx-auto">
            Experience what happens when policy cutover occurs while a $700 discount request is in flight.
          </p>
        </div>

        <div className="p-6 md:p-8 rounded-2xl bg-white border border-paper-200 shadow-sm space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Step 1 */}
            <div className="p-5 rounded-xl bg-paper-50 border border-paper-200 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-semibold text-graphite-subtle">01. INCOMING REQUEST</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-paper-200 text-graphite-main">GOLD TIER</span>
              </div>
              <div className="text-xl font-bold text-graphite-main">$700 Discount</div>
              <p className="text-xs text-graphite-muted">Client Acme Corp requested 14% override on Invoice #409.</p>
            </div>

            {/* Step 2 */}
            <div className="p-5 rounded-xl bg-paper-50 border border-paper-200 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-semibold text-graphite-subtle">02. MEMORY CUTOVER</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono ${interactiveRace !== "IDLE" ? "bg-amber-100 text-amber-800" : "bg-paper-200 text-graphite-main"}`}>
                  {interactiveRace === "IDLE" ? "ACTIVE: G17" : "CUTOVER: G18"}
                </span>
              </div>
              <div className="text-xl font-bold text-graphite-main">
                {interactiveRace === "IDLE" ? "Limit: $1500 (G17)" : "Limit: $500 (G18)"}
              </div>
              <p className="text-xs text-graphite-muted">
                {interactiveRace === "IDLE" ? "Agent reasons under G17." : "Policy committee tightened discount ceiling to $500!"}
              </p>
            </div>

            {/* Step 3 */}
            <div className="p-5 rounded-xl bg-paper-50 border border-paper-200 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-semibold text-graphite-subtle">03. QUOIN FENCE</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                  interactiveRace === "BLOCKED" ? "bg-rose-100 text-rose-800" : "bg-paper-200 text-graphite-main"
                }`}>
                  {interactiveRace === "BLOCKED" ? "GATE LOCKED" : "ARMED"}
                </span>
              </div>
              <div className="text-xl font-bold text-graphite-main">
                {interactiveRace === "BLOCKED" ? "FENCE BLOCKED" : "Comparing CAS"}
              </div>
              <p className="text-xs text-graphite-muted">
                {interactiveRace === "BLOCKED" ? "Generation mismatch detected (G17 != G18). Receipt invalidated." : "Read-after-write commit check."}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-paper-200">
            <div className="text-xs font-mono text-graphite-muted">
              Current Simulator State: <span className="font-semibold text-graphite-main">{interactiveRace}</span>
            </div>
            <div className="flex items-center gap-3">
              {interactiveRace === "IDLE" && (
                <button
                  onClick={() => setInteractiveRace("RACE_OCCURRED")}
                  className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-xs font-medium flex items-center gap-1.5 transition-all"
                >
                  <AlertTriangle className="w-3.5 h-3.5" /> Trigger In-Flight Policy Cutover (G17 &rarr; G18)
                </button>
              )}
              {interactiveRace === "RACE_OCCURRED" && (
                <button
                  onClick={() => setInteractiveRace("BLOCKED")}
                  className="px-4 py-2 rounded-lg bg-graphite-main hover:bg-black text-white text-xs font-medium flex items-center gap-1.5 transition-all"
                >
                  <Lock className="w-3.5 h-3.5" /> Attempt Commit at Gate
                </button>
              )}
              {interactiveRace === "BLOCKED" && (
                <button
                  onClick={() => setInteractiveRace("IDLE")}
                  className="px-4 py-2 rounded-lg bg-paper-200 hover:bg-paper-300 text-graphite-main text-xs font-medium flex items-center gap-1.5 transition-all"
                >
                  <RefreshCw className="w-3.5 h-3.5" /> Reset Simulation
                </button>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* 4. THE FOUR-PLANE ARCHITECTURE */}
      <section className="max-w-5xl mx-auto px-6 space-y-8">
        <div className="text-center space-y-2">
          <div className="text-xs font-mono uppercase tracking-widest text-emerald-600 font-semibold">Deep Architecture</div>
          <h2 className="text-3xl font-bold tracking-tight text-graphite-main">Four-Plane Separation</h2>
          <p className="text-sm text-graphite-muted max-w-xl mx-auto">
            Zero-trust separation between generative model reasoning and deterministic authority execution.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 rounded-xl bg-white border border-paper-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-blue-600">PLANE A: REASONING</span>
              <span className="text-[10px] font-mono bg-paper-100 px-2 py-0.5 rounded text-graphite-subtle">STRANDS SDK</span>
            </div>
            <h3 className="text-lg font-bold text-graphite-main">Strands Reasoning Agent</h3>
            <p className="text-xs text-graphite-muted leading-relaxed">
              Analyzes client intent, extracts structured variables, and proposes candidate operational actions. Untrusted for authority; cannot execute side effects or bypass gates.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-white border border-paper-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-emerald-600">PLANE B: AUTHORITY</span>
              <span className="text-[10px] font-mono bg-paper-100 px-2 py-0.5 rounded text-graphite-subtle">PURE PYTHON</span>
            </div>
            <h3 className="text-lg font-bold text-graphite-main">Deterministic Kernel</h3>
            <p className="text-xs text-graphite-muted leading-relaxed">
              Model-free evaluation engine. Computes canonical SHA-256 digests, issues cryptographically signed authority receipts, and enforces the Two-Phase Commit Gate.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-white border border-paper-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-purple-600">PLANE C: MEMORY</span>
              <span className="text-[10px] font-mono bg-paper-100 px-2 py-0.5 rounded text-graphite-subtle">AWS AGENTCORE</span>
            </div>
            <h3 className="text-lg font-bold text-graphite-main">AgentCore Memory</h3>
            <p className="text-xs text-graphite-muted leading-relaxed">
              Multi-tenant isolated namespaces (/quoin/tenant/policy) with structured metadata. Explicitly models asynchronous background consolidation lag.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-white border border-paper-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-graphite-main">PLANE D: EFFECTS</span>
              <span className="text-[10px] font-mono bg-paper-100 px-2 py-0.5 rounded text-graphite-subtle">IDEMPOTENT</span>
            </div>
            <h3 className="text-lg font-bold text-graphite-main">Action Execution Service</h3>
            <p className="text-xs text-graphite-muted leading-relaxed">
              Applies discounts, credits, and exceptions strictly upon receiving a valid single-use ExecutionPermit. Built-in deduplication ledger eliminates replay attacks.
            </p>
          </div>
        </div>
      </section>

      {/* 5. CALL TO ACTION */}
      <section className="max-w-5xl mx-auto px-6 text-center space-y-6">
        <div className="p-12 rounded-3xl bg-graphite-main text-white space-y-6 shadow-xl">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
            Inspect the live cutover console and test results.
          </h2>
          <p className="text-paper-300 max-w-xl mx-auto text-sm">
            Experience live in-flight cutover detection, review the 13 adversarial attacks, and explore the benchmark evidence.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <Link
              href="/console"
              className="px-6 py-3 rounded-lg bg-white text-graphite-main hover:bg-paper-100 font-semibold text-sm transition-all shadow"
            >
              Open Cutover Console
            </Link>
            <Link
              href="/proof"
              className="px-6 py-3 rounded-lg bg-paper-800 text-white hover:bg-paper-900 border border-paper-700 font-semibold text-sm transition-all"
            >
              View Proof &amp; Benchmarks
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
