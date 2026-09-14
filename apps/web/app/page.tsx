"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Hero } from "@/components/Hero";
import { ScrubTimeline } from "@/components/ScrubTimeline";
import { ArchitectureVisual } from "@/components/ArchitectureVisual";
import { EpochRace } from "@/components/EpochRace";
import { ProofMetricGrid } from "@/components/ProofMetric";
import { EvidenceDrawer } from "@/components/EvidenceDrawer";
import {
  Terminal,
  Bug,
  GitCommit,
  FileCheck,
  FileText,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Lock,
  Database,
  Cpu,
  RefreshCw,
} from "lucide-react";

export default function LandingPage() {
  const [evidenceOpen, setEvidenceOpen] = useState(false);

  return (
    <div className="space-y-0 pb-0">
      {/* 1. Cinematic Full-Bleed Hero */}
      <Hero />

      {/* 2. Infinite Ticker Marquee */}
      <div className="ticker" aria-hidden="true">
        <div className="track">
          <span>
            EPOCH <b>G18 ACTIVE</b> · <span className="g">AUTHORITATIVE</span>
          </span>
          <span>
            CAS CONDITION <b>active_epoch = 17</b> · <span className="g">COMMITTED</span>
          </span>
          <span>
            BENCHMARK <b>100 / 100 PROOFS</b> · <span className="g">0 STALE EXECUTIONS</span>
          </span>
          <span>
            ATTACK SUITE <b>27 / 27 VECTORS</b> · <span className="g">100% NEUTRALIZED</span>
          </span>
          <span>
            OVERHEAD P50 <b>0.60 MS</b> · <span className="g">SUB-MILLISECOND FENCE</span>
          </span>
          <span>
            BEDROCK NOVA <b>us.amazon.nova-lite-v1:0</b> · <span className="g">ACTIVE REASONING</span>
          </span>
          <span>
            PERMIT <b>7f8a9e…10c2</b> · <span className="g">VALIDATED ON-CHAIN</span>
          </span>
          {/* Duplicate track for seamless infinite loop */}
          <span>
            EPOCH <b>G18 ACTIVE</b> · <span className="g">AUTHORITATIVE</span>
          </span>
          <span>
            CAS CONDITION <b>active_epoch = 17</b> · <span className="g">COMMITTED</span>
          </span>
          <span>
            BENCHMARK <b>100 / 100 PROOFS</b> · <span className="g">0 STALE EXECUTIONS</span>
          </span>
          <span>
            ATTACK SUITE <b>27 / 27 VECTORS</b> · <span className="g">100% NEUTRALIZED</span>
          </span>
          <span>
            OVERHEAD P50 <b>0.60 MS</b> · <span className="g">SUB-MILLISECOND FENCE</span>
          </span>
          <span>
            BEDROCK NOVA <b>us.amazon.nova-lite-v1:0</b> · <span className="g">ACTIVE REASONING</span>
          </span>
          <span>
            PERMIT <b>7f8a9e…10c2</b> · <span className="g">VALIDATED ON-CHAIN</span>
          </span>
        </div>
      </div>

      {/* 3. Interactive Timeline Scrubber */}
      <ScrubTimeline />

      {/* 4. Problem Stack (.pstack) */}
      <section className="py-24 bg-[var(--bg)] border-b border-[var(--line)] transition-colors duration-200">
        <div className="max-w-[1400px] mx-auto px-6 sm:px-10 lg:px-14">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-[var(--t1)] tracking-tight max-w-2xl">
            Console logs break when agents move money.
          </h2>
          <div className="pstack">
            <div className="row">
              <span className="num">/ 01</span>
              <div>
                <h3 className="text-xl sm:text-2xl font-bold text-[var(--t1)]">Eventual consistency is not authority</h3>
                <p className="mt-2 text-sm sm:text-base text-[var(--t2)] leading-relaxed">
                  Vector stores and memory engines take 100–300 ms to propagate policy updates. During this visibility
                  window, agents blindly dispatch high-value actions based on stale assumptions.
                </p>
              </div>
            </div>
            <div className="row">
              <span className="num">/ 02</span>
              <div>
                <h3 className="text-xl sm:text-2xl font-bold text-[var(--t1)]">Execution without cryptographic lease</h3>
                <p className="mt-2 text-sm sm:text-base text-[var(--t2)] leading-relaxed">
                  Decoupled LLM reasoning can propose any action, but traditional execution gateways lack an unforgeable,
                  time-bounded proof connecting that proposal to an authoritative policy epoch.
                </p>
              </div>
            </div>
            <div className="row">
              <span className="num">/ 03</span>
              <div>
                <h3 className="text-xl sm:text-2xl font-bold text-[var(--t1)]">Forensic blackouts and unaccountability</h3>
                <p className="mt-2 text-sm sm:text-base text-[var(--t2)] leading-relaxed">
                  When an unauthorized liquidation or data transfer occurs, standard application logs cannot prove what
                  policy the model witnessed at that exact microsecond. QUOIN seals every decision into an immutable SHA-256
                  hash chain.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 5. Bento Grid (.bento) */}
      <section id="evidence" className="py-24 bg-[var(--bg2)] border-b border-[var(--line)] transition-colors duration-200">
        <div className="max-w-[1400px] mx-auto px-6 sm:px-10 lg:px-14">
          <div className="max-w-2xl mb-12">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-[var(--t1)] tracking-tight mb-3">
              Every decision becomes provable evidence.
            </h2>
            <p className="text-sm sm:text-base text-[var(--t2)]">
              One permit per consequential action: evaluated, two-phase leased, and anchored in DynamoDB. Real benchmark values below.
            </p>
          </div>

          <div className="bento">
            {/* Cell 1: Two-Phase Commit Permit */}
            <div className="cell-shell c-packet">
              <div className="cell">
                <div className="cell-placeholder">
                  <span className="placeholder-text" style={{ ["--c" as any]: "var(--rec)" }}>
                    PERMIT
                  </span>
                </div>
                <div className="cell-content">
                  <div>
                    <span className="pill o">Two-Phase Lease · Seq 042</span>
                    <div className="data mt-4 space-y-1">
                      <div>
                        <span className="k font-mono text-[0.62rem] text-[var(--t3)] mr-4 uppercase">Agent ID</span>
                        <span className="v font-mono text-xs text-[var(--t1)]">risk-arbitrage-01</span>
                      </div>
                      <div>
                        <span className="k font-mono text-[0.62rem] text-[var(--t3)] mr-4 uppercase">Epoch Target</span>
                        <span className="v font-mono text-xs text-[var(--t1)]">18 (G18 Active Fence)</span>
                      </div>
                      <div>
                        <span className="k font-mono text-[0.62rem] text-[var(--t3)] mr-4 uppercase">Lease TTL</span>
                        <span className="v font-mono text-xs text-[var(--t1)]">5,000 ms (HMAC-SHA256 Signed)</span>
                      </div>
                      <div>
                        <span className="k font-mono text-[0.62rem] text-[var(--t3)] mr-4 uppercase">Permit Digest</span>
                        <span className="v font-mono text-xs text-[var(--proof)]">
                          7f8a9e10c2b5d4e3f1a0987654321fedcba09876
                        </span>
                      </div>
                    </div>
                  </div>
                  <p className="text-xs text-[var(--t2)]">
                    Two-Phase Commit fence validates policy preconditions before granting gateway dispatch rights.
                  </p>
                </div>
              </div>
            </div>

            {/* Cell 2: Verified Authority */}
            <div className="cell-shell c-verify">
              <div className="cell">
                <div className="cell-placeholder">
                  <span className="placeholder-text" style={{ ["--c" as any]: "var(--proof)" }}>
                    AUTHORITY
                  </span>
                </div>
                <div className="cell-content">
                  <div>
                    <span className="pill g">DynamoDB CAS</span>
                    <h3 className="text-lg font-bold text-[var(--t1)] mt-3">Atomic Condition Verification</h3>
                    <p className="text-xs text-[var(--t2)] mt-1">
                      ConditionExpression asserts active_epoch == prev_epoch. Zero race window under cutovers.
                    </p>
                  </div>
                  <p className="font-mono text-xs text-[var(--proof)]">
                    G_active = 18 ∧ CAS_status ≡ COMMITTED
                  </p>
                </div>
              </div>
            </div>

            {/* Cell 3: Decision Trace */}
            <div className="cell-shell c-fork">
              <div className="cell">
                <div className="cell-placeholder">
                  <span className="placeholder-text" style={{ ["--c" as any]: "var(--fork)" }}>
                    TRACE
                  </span>
                </div>
                <div className="cell-content">
                  <div>
                    <span className="pill b">Forensic Chain</span>
                    <h3 className="text-lg font-bold text-[var(--t1)] mt-3">Immutable SHA-256 Merkle Link</h3>
                    <p className="text-xs text-[var(--t2)] mt-1">
                      Every prompt, tool execution, and permit forms an unalterable causal timeline from genesis to settlement.
                    </p>
                  </div>
                  <p className="font-mono text-xs text-[var(--fork)]">
                    genesis &rarr; cutover &rarr; eval &rarr; permit &rarr; execute (0 errors)
                  </p>
                </div>
              </div>
            </div>

            {/* Cell 4: Tamper Fail-Closed */}
            <div className="cell-shell c-mismatch">
              <div className="cell">
                <div className="cell-placeholder">
                  <span className="placeholder-text" style={{ ["--c" as any]: "var(--err)" }}>
                    TAMPER
                  </span>
                </div>
                <div className="cell-content">
                  <div>
                    <span className="pill r">Fail-Closed</span>
                    <h3 className="text-lg font-bold text-[var(--t1)] mt-3">Signature Mismatch Rejection</h3>
                    <p className="text-xs text-[var(--t2)] mt-1">
                      Payload or timestamp modification immediately breaks HMAC verification. Gateways reject execution.
                    </p>
                  </div>
                  <p className="font-mono text-xs text-[var(--err)] line-through">
                    8f02c1aa…94d3e0 ≠ 7f8a9e…10c2
                  </p>
                </div>
              </div>
            </div>

            {/* Cell 5: AWS Bedrock Reasoning */}
            <div className="cell-shell c-contract">
              <div className="cell">
                <div className="cell-placeholder">
                  <span className="placeholder-text" style={{ ["--c" as any]: "#FFD700" }}>
                    BEDROCK
                  </span>
                </div>
                <div className="cell-content">
                  <div>
                    <span className="pill o">Nova Lite</span>
                    <h3 className="text-lg font-bold text-[var(--t1)] mt-3">Structured Reasoning</h3>
                    <p className="text-xs text-[var(--t2)] mt-1">
                      us.amazon.nova-lite-v1:0 enforces policy schema adherence.
                    </p>
                  </div>
                  <Link href="/console" className="font-mono text-[0.68rem] text-[var(--rec)] uppercase tracking-wider hover:underline">
                    Launch in Console &rarr;
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 6. Controlled Causal Benchmark Proof Metrics Grid */}
      <section className="py-20 border-b border-[var(--line)] bg-[var(--bg)] transition-colors duration-200">
        <div className="max-w-[1400px] mx-auto px-6 sm:px-10 lg:px-14">
          <div className="mb-10 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <div>
              <p className="text-xs font-mono uppercase text-[var(--proof)] font-semibold tracking-wider">
                Controlled Causal Benchmark
              </p>
              <h2 className="text-2xl sm:text-3xl font-bold text-[var(--t1)] tracking-tight mt-1">
                Measured Head-to-Head Performance (100 Scenarios)
              </h2>
            </div>
            <button
              onClick={() => setEvidenceOpen(true)}
              className="btn"
            >
              <FileText className="w-3.5 h-3.5 text-[var(--proof)]" />
              <span>Inspect Raw Evidence JSON</span>
              <span className="chip">↗</span>
            </button>
          </div>

          <ProofMetricGrid />
        </div>
      </section>

      {/* 7. System Architecture & Product Flow Visuals */}
      <ArchitectureVisual />

      {/* 8. Interactive Epoch Race Simulator */}
      <EpochRace />

      {/* 9. SDK Integration Strip */}
      <section id="sdk" className="py-24 bg-[var(--bg2)] border-b border-[var(--line)] transition-colors duration-200">
        <div className="max-w-[1400px] mx-auto px-6 sm:px-10 lg:px-14">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            <div className="lg:col-span-6">
              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-[var(--t1)] tracking-tight mb-4">
                Five lines to fence your autonomous agent.
              </h2>
              <p className="text-base text-[var(--t2)] leading-relaxed mb-6">
                Works seamlessly with any Python or Node.js agent. The full two-phase verification and causal ledger runs
                locally for testing or on AWS DynamoDB &amp; Bedrock for production.
              </p>
              <div className="grid grid-cols-2 gap-3 font-mono text-xs">
                <div className="p-3 bg-[var(--bg)] border border-[var(--line)] text-[var(--t1)] flex items-center gap-2">
                  <span className="text-[var(--proof)]">✓</span> QUOIN_ACQUIRE_PERMIT
                </div>
                <div className="p-3 bg-[var(--bg)] border border-[var(--line)] text-[var(--t1)] flex items-center gap-2">
                  <span className="text-[var(--proof)]">✓</span> QUOIN_VERIFY_LEASE
                </div>
                <div className="p-3 bg-[var(--bg)] border border-[var(--line)] text-[var(--t1)] flex items-center gap-2">
                  <span className="text-[var(--proof)]">✓</span> QUOIN_FORCE_CUTOVER
                </div>
                <div className="p-3 bg-[var(--bg)] border border-[var(--line)] text-[var(--t1)] flex items-center gap-2">
                  <span className="text-[var(--proof)]">✓</span> QUOIN_FORENSIC_ANCHOR
                </div>
              </div>
            </div>

            <div className="lg:col-span-6">
              <div className="bg-[var(--bg)] border border-[var(--line)] p-6 font-mono text-xs leading-relaxed overflow-x-auto shadow-2xl transition-colors duration-200">
                <p className="text-[var(--t3)] mb-3">// Plane B Two-Phase Commit Fence</p>
                <p>
                  <span className="text-[var(--rec)]">from</span> quoin.authority{" "}
                  <span className="text-[var(--rec)]">import</span> DynamoAuthorityLedger
                </p>
                <p>
                  <span className="text-[var(--rec)]">from</span> quoin.kernel{" "}
                  <span className="text-[var(--rec)]">import</span> PlaneBFenceKernel
                </p>
                <br />
                <p className="text-[var(--t3)]">// 1. Evaluate proposal against authoritative epoch</p>
                <p>
                  decision = kernel.<span className="text-[var(--proof)]">evaluate_precondition</span>(
                </p>
                <p className="pl-4">proposal_epoch=18, agent_id=<span className="text-[var(--t1)]">"risk-arb-01"</span></p>
                <p>)</p>
                <br />
                <p className="text-[var(--t3)]">// 2. Acquire cryptographic execution lease</p>
                <p>
                  permit = kernel.<span className="text-[var(--proof)]">issue_permit</span>(decision, ttl_ms=5000)
                </p>
                <p className="text-[var(--t3)]">// 3. Dispatch to Execution Gateway with verified lease</p>
                <p>
                  result = gateway.<span className="text-[var(--proof)]">execute_with_permit</span>(permit, action_payload)
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 10. Deep-Dive Exploration Grid */}
      <section className="py-24 bg-[var(--bg)] border-b border-[var(--line)] transition-colors duration-200">
        <div className="max-w-[1400px] mx-auto px-6 sm:px-10 lg:px-14">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <p className="text-xs font-mono uppercase text-[var(--proof)] font-semibold tracking-wider">
              Complete System Exploration
            </p>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-[var(--t1)] tracking-tight mt-2">
              Explore Every Dimension of the QUOIN Architecture
            </h2>
            <p className="mt-3 text-sm text-[var(--t2)]">
              Interactive console, 27 adversarial vector neutralizations, cryptographic forensic timeline, and audited proof manifest.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Card 1: Console */}
            <Link
              href="/console"
              className="group p-6 border border-[var(--line)] bg-[var(--bg2)] hover:border-[var(--proof)]/60 hover:bg-[var(--core)] transition-all flex flex-col justify-between"
            >
              <div>
                <div className="w-10 h-10 bg-[var(--proof)]/10 text-[var(--proof)] border border-[var(--proof)]/30 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                  <Terminal className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-[var(--t1)]">Operator Console</h3>
                <p className="text-xs text-[var(--t2)] mt-2 leading-relaxed">
                  Publish authoritative policy cutovers (G17 &rarr; G18), evaluate requests under live Bedrock reasoning, and observe two-phase permit issuance.
                </p>
              </div>
              <div className="mt-6 flex items-center text-xs font-mono text-[var(--proof)] group-hover:translate-x-1 transition-transform">
                <span>Launch Console &rarr;</span>
              </div>
            </Link>

            {/* Card 2: Break It Lab */}
            <Link
              href="/lab"
              className="group p-6 border border-[var(--line)] bg-[var(--bg2)] hover:border-[var(--rec)]/60 hover:bg-[var(--core)] transition-all flex flex-col justify-between"
            >
              <div>
                <div className="w-10 h-10 bg-[var(--rec)]/10 text-[var(--rec)] border border-[var(--rec)]/30 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                  <Bug className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-[var(--t1)]">Break It Lab (27 Attacks)</h3>
                <p className="text-xs text-[var(--t2)] mt-2 leading-relaxed">
                  Execute all 27 distinct failure, race, tamper, replay, and rollback vectors across Plane A, B, C, and D. 100% neutralized.
                </p>
              </div>
              <div className="mt-6 flex items-center text-xs font-mono text-[var(--rec)] group-hover:translate-x-1 transition-transform">
                <span>Run Attack Suite &rarr;</span>
              </div>
            </Link>

            {/* Card 3: Decision Trace */}
            <Link
              href="/trace"
              className="group p-6 border border-[var(--line)] bg-[var(--bg2)] hover:border-[var(--fork)]/60 hover:bg-[var(--core)] transition-all flex flex-col justify-between"
            >
              <div>
                <div className="w-10 h-10 bg-[var(--fork)]/10 text-[var(--fork)] border border-[var(--fork)]/30 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                  <GitCommit className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-[var(--t1)]">Decision Trace</h3>
                <p className="text-xs text-[var(--t2)] mt-2 leading-relaxed">
                  Forensic timeline with cryptographically chained SHA-256 event digests. Verify full execution history from genesis to head.
                </p>
              </div>
              <div className="mt-6 flex items-center text-xs font-mono text-[var(--fork)] group-hover:translate-x-1 transition-transform">
                <span>Verify Chain &rarr;</span>
              </div>
            </Link>

            {/* Card 4: Proof Center */}
            <Link
              href="/proof"
              className="group p-6 border border-[var(--line)] bg-[var(--bg2)] hover:border-purple-500/60 hover:bg-[var(--core)] transition-all flex flex-col justify-between"
            >
              <div>
                <div className="w-10 h-10 bg-purple-500/10 text-purple-400 border border-purple-500/30 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                  <FileCheck className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-[var(--t1)]">Proof Center</h3>
                <p className="text-xs text-[var(--t2)] mt-2 leading-relaxed">
                  Live dynamic verifier status, 100-scenario causal benchmark table, empirical AgentCore memory visibility data, and cryptographic proofs.
                </p>
              </div>
              <div className="mt-6 flex items-center text-xs font-mono text-purple-400 group-hover:translate-x-1 transition-transform">
                <span>Inspect Proofs &rarr;</span>
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* 11. Stark Editorial Contrast Brand Footer (.brand-footer) */}
      <footer className="brand-footer transition-colors duration-200">
        <div className="max-w-[1400px] mx-auto px-6 sm:px-10 lg:px-14 flex flex-col sm:flex-row justify-between items-center gap-6">
          <div>
            <p className="font-bold text-sm tracking-wider uppercase">
              QUOIN <b>·</b> DETERMINISTIC POLICY-GENERATION FENCE
            </p>
            <p className="text-xs mt-1">
              BUILT ON <b>AWS DYNAMODB &amp; BEDROCK NOVA</b> · ZERO STALE EXECUTIONS · 100/100 AUDITED BENCHMARK PROOFS
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-4 text-xs font-mono">
            <Link href="/console">Console</Link>
            <span>·</span>
            <Link href="/lab">Break It Lab</Link>
            <span>·</span>
            <Link href="/trace">Decision Trace</Link>
            <span>·</span>
            <Link href="/proof">Proof Center</Link>
          </div>
        </div>
      </footer>

      {/* Evidence Drawer Modal */}
      <EvidenceDrawer isOpen={evidenceOpen} onClose={() => setEvidenceOpen(false)} />
    </div>
  );
}

