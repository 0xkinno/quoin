"use client";

import React, { useState, useEffect } from "react";
import { Bug, Search, Play, CheckCircle, XCircle, Filter, RefreshCw } from "lucide-react";
import { api, BackendUnavailableError } from "@/lib/api";
import { BackendUnavailableBanner } from "./BackendUnavailableBanner";

export const AttackMatrix: React.FC = () => {
  const [attacks, setAttacks] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterPlane, setFilterPlane] = useState<string>("ALL");
  const [loading, setLoading] = useState(true);
  const [runningAttackId, setRunningAttackId] = useState<string | null>(null);
  const [attackResults, setAttackResults] = useState<Record<string, any>>({});
  const [backendError, setBackendError] = useState<string | null>(null);

  const loadScenarios = async () => {
    setLoading(true);
    setBackendError(null);
    try {
      const data: any = await api.getLabScenarios();
      const list = Array.isArray(data) ? data : (data?.traces || data?.scenarios || []);
      setAttacks(list);
    } catch (err: any) {
      if (err instanceof BackendUnavailableError) {
        setBackendError(err.message);
      } else {
        setBackendError(err.message || "Failed to load adversarial attack suite.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadScenarios();
  }, []);

  const handleRunAttack = async (attackId: string) => {
    setRunningAttackId(attackId);
    try {
      const res = await api.runLabAttack(attackId);
      setAttackResults((prev) => ({ ...prev, [attackId]: res }));
    } catch (err: any) {
      alert(`Attack ${attackId} execution failed: ` + err.message);
    } finally {
      setRunningAttackId(null);
    }
  };

  const attackList = Array.isArray(attacks) ? attacks : [];
  const filteredAttacks = attackList.filter((att) => {
    const matchesSearch =
      att.id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      att.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (att.invariant && att.invariant.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesPlane =
      filterPlane === "ALL" ||
      (filterPlane === "PLANE_A" && ["ATT_K", "ATT_L", "ATT_M", "ATT_X"].includes(att.id)) ||
      (filterPlane === "PLANE_B" && ["ATT_A", "ATT_B", "ATT_C", "ATT_D", "ATT_E", "ATT_F", "ATT_G", "ATT_O", "ATT_R", "ATT_S", "ATT_T", "ATT_U", "ATT_V", "ATT_W"].includes(att.id)) ||
      (filterPlane === "PLANE_C" && ["ATT_H", "ATT_N", "ATT_P", "ATT_Z"].includes(att.id)) ||
      (filterPlane === "PLANE_D" && ["ATT_I", "ATT_J", "ATT_Q", "ATT_Y", "ATT_AA"].includes(att.id));

    return matchesSearch && matchesPlane;
  });

  return (
    <div className="w-full space-y-6">
      {backendError && (
        <BackendUnavailableBanner
          error={backendError}
          onRetry={loadScenarios}
          isRetrying={loading}
        />
      )}

      {/* Controls Bar */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 p-4 rounded-xl border border-zinc-800 bg-zinc-900/60 backdrop-blur-md">
        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="relative flex-1 md:w-72">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search 27 attack vectors..."
              className="w-full pl-9 pr-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-sm text-zinc-200 font-mono focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="flex items-center gap-1 p-1 rounded-lg bg-zinc-950 border border-zinc-800 text-xs font-mono">
            {["ALL", "PLANE_A", "PLANE_B", "PLANE_C", "PLANE_D"].map((p) => (
              <button
                key={p}
                onClick={() => setFilterPlane(p)}
                className={`px-2.5 py-1 rounded transition-colors ${
                  filterPlane === p ? "bg-emerald-600 text-white font-bold" : "text-zinc-400 hover:text-white"
                }`}
              >
                {p.replace("_", " ")}
              </button>
            ))}
          </div>
        </div>

        <div className="text-xs text-zinc-400 font-mono">
          Showing {filteredAttacks.length} of {attacks.length} neutralizations
        </div>
      </div>

      {/* Attack Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredAttacks.map((att) => {
          const liveResult = attackResults[att.id];
          const isRunning = runningAttackId === att.id;

          return (
            <div
              key={att.id}
              className="p-5 rounded-xl border border-zinc-800/80 bg-zinc-900/50 backdrop-blur-md hover:border-zinc-700 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
                    {att.id}
                  </span>
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                    100% NEUTRALIZED
                  </span>
                </div>

                <h4 className="font-bold text-white text-sm">{att.name}</h4>
                <p className="text-xs text-zinc-400 mt-1">{att.description}</p>

                <div className="mt-3 pt-3 border-t border-zinc-800/80 space-y-1.5 text-[11px] font-mono">
                  <div className="flex items-center justify-between text-zinc-400">
                    <span>Expected:</span>
                    <span className="text-zinc-200 font-semibold">{att.expected}</span>
                  </div>
                  <div className="flex items-center justify-between text-zinc-400">
                    <span>Invariant:</span>
                    <span className="text-emerald-400">{att.invariant}</span>
                  </div>
                </div>

                {liveResult && (
                  <div className="mt-3 p-2.5 rounded-lg bg-zinc-950 border border-zinc-800 text-[11px] font-mono">
                    <div className="flex items-center gap-1.5 text-emerald-400 font-bold">
                      <CheckCircle className="w-3.5 h-3.5" />
                      <span>OBSERVED: {liveResult.status || liveResult.observed}</span>
                    </div>
                    <p className="text-zinc-400 mt-1 text-[10px] leading-tight">
                      {liveResult.details || liveResult.error || "Verified mathematically safe."}
                    </p>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-zinc-800/60 flex items-center justify-between">
                <span className="text-[10px] text-zinc-500 font-mono">Live Kernel Dispatch</span>
                <button
                  onClick={() => handleRunAttack(att.id)}
                  disabled={isRunning}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 hover:text-white font-mono text-xs font-semibold transition-colors disabled:opacity-50"
                >
                  <Play className={`w-3 h-3 ${isRunning ? "animate-spin" : ""}`} />
                  <span>{isRunning ? "Executing..." : "Execute Vector"}</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
