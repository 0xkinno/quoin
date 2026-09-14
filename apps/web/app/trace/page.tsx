"use client";

import React from "react";
import { TraceTimeline } from "@/components/TraceTimeline";
import { GitCommit, ShieldCheck, Lock, Hash, Layers } from "lucide-react";

export default function DecisionTracePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-zinc-800/80">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono uppercase text-cyan-400 font-semibold tracking-wider mb-2">
            <GitCommit className="w-4 h-4" />
            <span>Plane B & Proof Plane Verification</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Decision Trace & Forensic Timeline
          </h1>
          <p className="mt-2 text-sm text-zinc-400 max-w-3xl leading-relaxed">
            Every consequential action path generates an append-only, cryptographically chained sequence of events.
            Any mutation, payload alteration, or temporal race breaks the SHA-256 chain and marks the trace as <strong className="text-rose-400">TRACE ALTERED</strong>.
          </p>
        </div>

        <div className="flex items-center gap-3 p-3 rounded-xl border border-zinc-800 bg-zinc-900/60 text-xs font-mono">
          <Hash className="w-4 h-4 text-emerald-400" />
          <div className="truncate max-w-[240px]">
            <span className="text-zinc-500">CHAINING FORMULA:</span>
            <p className="text-emerald-300 font-bold">H(H_(n-1) || Event_n)</p>
          </div>
        </div>
      </div>

      {/* Chaining Principle Callouts */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/40 font-mono text-xs">
          <div className="flex items-center gap-2 text-emerald-400 font-bold mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Deterministic Hashing</span>
          </div>
          <p className="text-zinc-400 font-sans text-xs mt-1">
            Canonical sorted-key JSON serialization ensures zero float or whitespace ambiguity.
          </p>
        </div>

        <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/40 font-mono text-xs">
          <div className="flex items-center gap-2 text-cyan-400 font-bold mb-1">
            <Lock className="w-4 h-4" />
            <span>Genesis Hash Anchor</span>
          </div>
          <p className="text-zinc-400 font-sans text-xs mt-1">
            Chaining starts strictly at 64-zero genesis string, enforcing complete chronological lineage.
          </p>
        </div>

        <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/40 font-mono text-xs">
          <div className="flex items-center gap-2 text-purple-400 font-bold mb-1">
            <Layers className="w-4 h-4" />
            <span>Cross-Plane Audit Trail</span>
          </div>
          <p className="text-zinc-400 font-sans text-xs mt-1">
            Ties Plane A proposal, Plane B fence evaluation, and Plane D execution into a single timeline.
          </p>
        </div>
      </div>

      {/* Main Interactive Timeline Component */}
      <TraceTimeline />
    </div>
  );
}
