"use client";

import React from "react";
import { Layers, Shield, Cpu, Database, CheckCircle2 } from "lucide-react";

export const ArchitectureVisual: React.FC = () => {
  const planes = [
    {
      plane: "Plane A",
      name: "Cognitive Reasoning Plane",
      tech: "Amazon Bedrock Nova Lite & Strands SDK",
      icon: Cpu,
      accent: "border-blue-500/30 bg-blue-500/5",
      badge: "border-blue-500/40 text-blue-600 dark:text-blue-400 bg-blue-500/10",
      description:
        "Interprets natural language business requests, reasons over visible context, and formulates candidate DecisionProposals. Strictly unprivileged.",
      invariant: "Proposal Only (No Side-Effect Capability)",
    },
    {
      plane: "Plane B",
      name: "Deterministic Kernel & CAS Gate",
      tech: "Pure Python / Rust Hasher / Monotonic Fence",
      icon: Shield,
      accent: "border-emerald-500/30 bg-emerald-500/5",
      badge: "border-emerald-500/40 text-emerald-600 dark:text-emerald-400 bg-emerald-500/10",
      description:
        "Model-free deterministic fence. Enforces generation equality, binds SHA-256 digests, and executes Phase 2 read-after-write CAS verification.",
      invariant: "G_proposal ≡ G_visible = G_active",
    },
    {
      plane: "Plane C",
      name: "Cognitive Memory & Authoritative Ledger",
      tech: "Amazon Bedrock AgentCore Memory & DynamoDB",
      icon: Database,
      accent: "border-purple-500/30 bg-purple-500/5",
      badge: "border-purple-500/40 text-purple-600 dark:text-purple-400 bg-purple-500/10",
      description:
        "Stores policy generations, authoritatively versions active epochs with DynamoDB conditional writes, and exposes episodic tenant memory.",
      invariant: "Atomic CAS Epoch Cutover & Linear Durability",
    },
    {
      plane: "Plane D",
      name: "Operational Action Service",
      tech: "Single-Use ExecutionPermits & Idempotency Vault",
      icon: CheckCircle2,
      accent: "border-amber-500/30 bg-amber-500/5",
      badge: "border-amber-500/40 text-amber-600 dark:text-amber-400 bg-amber-500/10",
      description:
        "Executes real enterprise side effects (commercial discounts, invoices, refunds). Refuses any request without a valid signed ExecutionPermit.",
      invariant: "Zero Execution Without Verified Permit",
    },
  ];

  return (
    <section className="py-20 border-b border-[var(--line)] bg-[var(--bg)] transition-colors duration-200">
      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 lg:px-14">
        {/* Section Header */}
        <div className="mb-12">
          <div className="chip-eyebrow mb-3">
            <i />
            <span>ARCHITECTURAL RIGOR · ZERO-TRUST TOPOLOGY</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-[var(--t1)]">
            Four-Plane System Topology
          </h2>
          <p className="mt-3 text-base text-[var(--t2)] max-w-3xl leading-relaxed">
            Zero-trust separation between generative LLM reasoning and authoritative side-effect execution.
            Execution authority is cryptographically isolated from reasoning outputs.
          </p>
        </div>

        {/* 4 Planes Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {planes.map((p) => {
            const Icon = p.icon;
            return (
              <div
                key={p.plane}
                className={`p-6 border rounded-sm transition-all hover:border-[var(--t1)]/40 flex flex-col justify-between ${p.accent}`}
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span
                      className={`font-mono text-[0.68rem] tracking-wider uppercase font-bold px-2 py-0.5 border ${p.badge}`}
                    >
                      {p.plane}
                    </span>
                    <Icon className="w-4 h-4 opacity-70 text-[var(--t1)]" />
                  </div>

                  <h3 className="font-bold text-[var(--t1)] text-base tracking-tight mb-1">
                    {p.name}
                  </h3>
                  <p className="text-[0.72rem] font-mono text-[var(--t3)] mb-4">
                    {p.tech}
                  </p>
                  <p className="text-xs text-[var(--t2)] leading-relaxed mb-6">
                    {p.description}
                  </p>
                </div>

                <div className="pt-3 border-t border-[var(--line)]">
                  <span className="text-[0.65rem] font-mono uppercase tracking-wider text-[var(--t3)] block mb-1">
                    Invariant Guard:
                  </span>
                  <code className="text-[0.72rem] font-mono text-[var(--t1)] font-semibold block">
                    {p.invariant}
                  </code>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
