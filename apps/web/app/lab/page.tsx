"use client";

import React, { useState } from "react";
import { AttackMatrix } from "@/components/AttackMatrix";
import { Bug, ShieldCheck, ShieldAlert, Zap, Terminal, FileText } from "lucide-react";
import { EvidenceDrawer } from "@/components/EvidenceDrawer";

export default function BreakItLabPage() {
  const [evidenceOpen, setEvidenceOpen] = useState(false);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-zinc-800/80">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono uppercase text-rose-400 font-semibold tracking-wider mb-2">
            <Bug className="w-4 h-4" />
            <span>Adversarial Break Suite</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Break It Lab: 27 Adversarial Attack Classes
          </h1>
          <p className="mt-2 text-sm text-zinc-400 max-w-3xl leading-relaxed">
            Every consequential action path is evaluated against 27 distinct failure, race, tamper, replay, and rollback vectors across Plane A, B, C, and D.
          </p>
        </div>

        <button
          onClick={() => setEvidenceOpen(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300 hover:text-white font-mono text-xs font-medium transition-colors self-start md:self-auto"
        >
          <FileText className="w-4 h-4 text-emerald-400" />
          <span>Inspect Evidence Traces</span>
        </button>
      </div>

      {/* Summary Stats Ribbons */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 font-mono">
        <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/40">
          <span className="text-xs text-zinc-400">Total Vectors</span>
          <p className="text-2xl font-bold text-white mt-1">27 Classes</p>
        </div>
        <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/10">
          <span className="text-xs text-emerald-400">Attacks Neutralized</span>
          <p className="text-2xl font-bold text-emerald-400 mt-1">27 / 27 (100%)</p>
        </div>
        <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/40">
          <span className="text-xs text-zinc-400">Unauthorized Effects</span>
          <p className="text-2xl font-bold text-white mt-1">0 Permitted</p>
        </div>
        <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/40">
          <span className="text-xs text-zinc-400">Planes Defended</span>
          <p className="text-2xl font-bold text-teal-400 mt-1">4 Isolated Planes</p>
        </div>
      </div>

      {/* Main 27-Attack Matrix Component */}
      <AttackMatrix />

      {/* Evidence Drawer Modal */}
      <EvidenceDrawer isOpen={evidenceOpen} onClose={() => setEvidenceOpen(false)} />
    </div>
  );
}
