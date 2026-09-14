"use client";

import React, { useState } from "react";
import { CheckCircle2, AlertTriangle, ShieldCheck, ArrowRight, ArrowLeft } from "lucide-react";

interface ScrubStep {
  label: string;
  kind: "OBSERVATION" | "HAZARD" | "INTERCEPTION" | "PERMIT" | "EXECUTION" | "PROOF";
  time: string;
  tag: string;
  summary: string;
  rows: [string, string, boolean?][];
  isProof?: boolean;
  isHazard?: boolean;
}

const steps: ScrubStep[] = [
  {
    label: "Policy Cutover",
    kind: "OBSERVATION",
    time: "14:32:11.000",
    tag: "AUTHORITY LEDGER",
    summary: "Operator published G18 cutover to DynamoDB with CAS condition check.",
    rows: [
      ["target_epoch", "18 (G18 - Volatility Throttle)"],
      ["prev_epoch", "17 (G17 - Aggressive Yield)"],
      ["condition", "active_epoch = 17 (CAS atomic update)"],
      ["ledger_status", "COMMITTED TO DYNAMODB", true],
    ],
  },
  {
    label: "Memory Lag Read",
    kind: "HAZARD",
    time: "14:32:11.042",
    tag: "AGENTCORE MEMORY",
    summary: "Agent reads semantic state from AgentCore memory during the visibility lag window.",
    isHazard: true,
    rows: [
      ["read_epoch", "17 (G17 - Stale Memory Read)"],
      ["actual_epoch", "18 (Authoritative Ledger)"],
      ["visibility_lag", "148 ms (Empirically Measured)"],
      ["hazard_status", "HIGH: STALE POLICY PROPOSAL IN-FLIGHT", false],
    ],
  },
  {
    label: "Plane B Interception",
    kind: "INTERCEPTION",
    time: "14:32:11.055",
    tag: "KERNEL FENCE",
    summary: "Plane B kernel fence checks proposal epoch against authoritative DynamoDB ledger.",
    rows: [
      ["assert_invariant", "G_proposal == G_active"],
      ["check_result", "FAIL: 17 != 18 (G_proposal is Stale)"],
      ["pre_commit_action", "HALT EXECUTION & FORCE RETRY"],
      ["fence_status", "UNAUTHORIZED SIDE EFFECT BLOCKED", true],
    ],
  },
  {
    label: "Permit Acquisition",
    kind: "PERMIT",
    time: "14:32:11.088",
    tag: "TWO-PHASE COMMIT",
    summary: "Agent refreshes state to G18 and acquires a cryptographically signed execution lease.",
    rows: [
      ["lease_id", "lease-7f8a9e10c2"],
      ["policy_epoch", "18 (G18 Confirmed)"],
      ["lease_ttl", "5,000 ms (HMAC-SHA256 Signed)"],
      ["permit_status", "CRYPTOGRAPHIC LEASE ISSUED", true],
    ],
  },
  {
    label: "Gateway Execution",
    kind: "EXECUTION",
    time: "14:32:11.094",
    tag: "PLANE D GATEWAY",
    summary: "Execution Plane D verifies permit signature and timestamp before dispatching trade.",
    rows: [
      ["target_venue", "Aave V3 USDY Liquidity Supply"],
      ["signature_check", "HMAC-SHA256 SIGNATURE VALID"],
      ["overhead_p50", "0.60 ms (Microsecond Latency)"],
      ["execution_status", "TRADE EXECUTED UNDER G18 RULES", true],
    ],
  },
  {
    label: "Forensic Settlement",
    kind: "PROOF",
    time: "14:32:11.102",
    tag: "DECISION TRACE",
    summary: "Complete execution record anchored into SHA-256 cryptographically chained forensic timeline.",
    isProof: true,
    rows: [
      ["trace_id", "trace-d890bfa1e944"],
      ["event_hash", "1bdc92ad0cb25d8cfdf228a4b5ceb523a00de7a61c"],
      ["merkle_prev", "c7d151c86e09a31a98242da018d9f58203f19e4a"],
      ["audit_status", "FORENSIC INTEGRITY VERIFIED (0 ERRORS)", true],
    ],
  },
];

export const ScrubTimeline: React.FC = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const activeStep = steps[activeIndex];

  return (
    <section id="scrub" className="relative z-1 py-24 bg-[var(--bg2)] border-b border-[var(--line)] overflow-hidden transition-colors duration-200">
      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 lg:px-14">
        {/* Header */}
        <div className="max-w-2xl mb-12">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-[var(--t1)] tracking-tight mb-3">
            Click to <em className="not-italic text-[var(--rec)]">scrub</em> the causal timeline.
          </h2>
          <p className="font-mono text-xs sm:text-sm text-[var(--t3)]">
            // the agent attempted execution on stale memory. quoin intercepted and forced two-phase policy alignment.
          </p>
        </div>

        {/* Timeline Rail */}
        <div className="relative h-28 mb-10 select-none">
          {/* Base rail line */}
          <div className="absolute left-0 right-0 top-7 h-[1px] bg-[var(--line)]" />

          {/* Filled progress line */}
          <div
            className="absolute left-0 top-7 h-[1px] bg-[var(--rec)] transition-all duration-300"
            style={{ width: `${(activeIndex / (steps.length - 1)) * 100}%` }}
          />

          {/* Scrub Stops */}
          <div className="relative w-full h-full">
            {steps.map((step, idx) => {
              const pct = (idx / (steps.length - 1)) * 100;
              const isCurrent = idx === activeIndex;
              const isPast = idx <= activeIndex;
              const isLast = idx === steps.length - 1;

              return (
                <button
                  key={idx}
                  onClick={() => setActiveIndex(idx)}
                  className="group absolute top-0 -translate-x-1/2 flex flex-col items-center focus:outline-none cursor-pointer"
                  style={{ left: `${pct}%` }}
                >
                  {/* Diamond Node */}
                  <div
                    className={`w-3.5 h-3.5 rotate-45 transition-all duration-300 mt-5 ${
                      isLast && isCurrent
                        ? "bg-[var(--proof)] border border-[var(--proof)] shadow-[0_0_12px_rgba(54,209,125,0.7)]"
                        : isCurrent
                        ? "bg-[var(--rec)] border border-[var(--rec)] shadow-[0_0_12px_rgba(255,90,31,0.7)] scale-125"
                        : isPast
                        ? "bg-[var(--rec)]/70 border border-[var(--rec)]/70"
                        : "bg-[var(--bg)] border border-[var(--t3)] group-hover:border-[var(--t1)]"
                    }`}
                  />

                  {/* Label */}
                  <span
                    className={`font-mono text-[0.62rem] tracking-wider uppercase whitespace-nowrap mt-4 transition-all duration-200 hidden md:block ${
                      isCurrent
                        ? isLast
                          ? "text-[var(--proof)] font-bold opacity-100"
                          : "text-[var(--t1)] font-semibold opacity-100"
                        : "text-[var(--t3)] opacity-60 group-hover:opacity-100"
                    }`}
                  >
                    {step.label}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Active Step Card */}
        <div className="bg-[var(--core)] border border-[var(--line)] p-8 sm:p-10 rounded-none shadow-2xl relative transition-colors duration-200">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-[var(--line)]">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span
                  className={`font-mono text-[0.62rem] tracking-[0.2em] uppercase px-2.5 py-1 border ${
                    activeStep.isHazard
                      ? "text-[#FF3B30] border-[#FF3B30]/40 bg-[#FF3B30]/10"
                      : activeStep.isProof
                      ? "text-[var(--proof)] border-[var(--proof)]/40 bg-[var(--proof)]/10"
                      : "text-[var(--rec)] border-[var(--rec)]/40 bg-[var(--rec)]/10"
                  }`}
                >
                  STEP 0{activeIndex + 1} // {activeStep.tag}
                </span>
                <span className="font-mono text-[0.65rem] text-[var(--t3)]">TIMESTAMP: {activeStep.time}</span>
              </div>
              <h3 className="text-2xl sm:text-3xl font-bold text-[var(--t1)] tracking-tight">{activeStep.label}</h3>
              <p className="text-sm text-[var(--t2)] mt-2 max-w-2xl leading-relaxed">{activeStep.summary}</p>
            </div>

            {/* Stepper Navigation Buttons */}
            <div className="flex items-center gap-3 self-start lg:self-auto">
              <button
                disabled={activeIndex === 0}
                onClick={() => setActiveIndex((prev) => Math.max(0, prev - 1))}
                className="btn disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <span>Prev Step</span>
                <span className="chip">←</span>
              </button>
              <button
                disabled={activeIndex === steps.length - 1}
                onClick={() => setActiveIndex((prev) => Math.min(steps.length - 1, prev + 1))}
                className="btn primary disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <span>Next Step</span>
                <span className="chip">→</span>
              </button>
            </div>
          </div>

          {/* Step Data Inspection Grid */}
          <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {activeStep.rows.map(([key, val, isOk], rIdx) => (
              <div key={rIdx} className="p-4 bg-[var(--bg)] border border-[var(--line)] flex flex-col justify-between transition-colors duration-200">
                <span className="font-mono text-[0.6rem] uppercase tracking-wider text-[var(--t3)]">{key}</span>
                <span
                  className={`font-mono text-xs sm:text-[0.78rem] mt-2 break-all ${
                    isOk === true
                      ? "text-[var(--proof)] font-medium"
                      : isOk === false
                      ? "text-[#FF3B30] font-medium"
                      : "text-[var(--t1)]"
                  }`}
                >
                  {val}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
