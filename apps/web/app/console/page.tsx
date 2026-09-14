"use client";

import React, { useState, useEffect } from "react";
import { Terminal, Shield, RefreshCw, CheckCircle2, XCircle, ArrowRight, Lock, Key, Layers, Zap } from "lucide-react";
import { api, BackendUnavailableError } from "@/lib/api";
import { BackendUnavailableBanner } from "@/components/BackendUnavailableBanner";

export default function ConsolePage() {
  const [activePolicy, setActivePolicy] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [backendError, setBackendError] = useState<string | null>(null);

  // Operational Request Form State
  const [clientTier, setClientTier] = useState("gold");
  const [discountAmount, setDiscountAmount] = useState(750);
  const [invoiceId, setInvoiceId] = useState("inv_4091");
  const [evalResult, setEvalResult] = useState<any>(null);
  const [commitResult, setCommitResult] = useState<any>(null);
  const [evaluating, setEvaluating] = useState(false);
  const [committing, setCommitting] = useState(false);

  // Cutover State
  const [cutoverTargetGen, setCutoverTargetGen] = useState(18);
  const [cutoverStandardLimit, setCutoverStandardLimit] = useState(400);
  const [cutoverGoldLimit, setCutoverGoldLimit] = useState(900);

  const loadPolicy = async () => {
    setLoading(true);
    setBackendError(null);
    try {
      const data = await api.getPolicies();
      setActivePolicy(data);
      if (data?.generation) {
        setCutoverTargetGen(data.generation + 1);
      }
    } catch (err: any) {
      if (err instanceof BackendUnavailableError) {
        setBackendError(err.message);
      } else {
        setBackendError(err.message || "Failed to load active policy authority.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPolicy();
  }, []);

  const handlePublishCutover = async () => {
    setLoading(true);
    setBackendError(null);
    try {
      const payload = {
        tenant_id: "agency_operations",
        generation: Number(cutoverTargetGen),
        rules: [
          { client_tier: "standard", max_discount_amount: Number(cutoverStandardLimit), max_discount_percentage: 10.0 },
          { client_tier: "gold", max_discount_amount: Number(cutoverGoldLimit), max_discount_percentage: 20.0 },
          { client_tier: "silver", max_discount_amount: 500.0, max_discount_percentage: 15.0 },
          { client_tier: "platinum", max_discount_amount: 2500.0, max_discount_percentage: 25.0, requires_escalation: true },
        ],
        scope: "commercial_discount",
      };
      await api.publishPolicy(payload);
      await loadPolicy();
      alert(`Successfully published authoritative cutover to Generation G${cutoverTargetGen}!`);
    } catch (err: any) {
      alert("Policy cutover failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluateRequest = async () => {
    setEvaluating(true);
    setEvalResult(null);
    setCommitResult(null);
    try {
      const reqPayload = {
        request_id: `req_${Date.now().toString().slice(-6)}`,
        tenant_id: "agency_operations",
        client_id: `cust_${clientTier}_01`,
        client_tier: clientTier,
        amount: Number(discountAmount),
        action: "apply_discount",
        invoice_id: invoiceId,
        discount_percentage: 15.0,
      };
      const res = await api.evaluateRequest(reqPayload);
      setEvalResult({ ...res, requestPayload: reqPayload });
    } catch (err: any) {
      alert("Evaluation failed: " + err.message);
    } finally {
      setEvaluating(false);
    }
  };

  const handleCommitRequest = async () => {
    if (!evalResult?.receipt) {
      alert("Cannot commit: No valid authority receipt available.");
      return;
    }
    setCommitting(true);
    try {
      const payload = {
        receipt: evalResult.receipt,
        request_payload: evalResult.requestPayload,
        proposal: evalResult.proposal,
      };
      const res = await api.commitRequest(payload);
      setCommitResult(res);
    } catch (err: any) {
      alert("Commit gate failed: " + err.message);
    } finally {
      setCommitting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-zinc-800/80">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono uppercase text-emerald-400 font-semibold tracking-wider mb-2">
            <Terminal className="w-4 h-4" />
            <span>Interactive Operational Plane</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Authority Cutover & Execution Console
          </h1>
          <p className="mt-2 text-sm text-zinc-400 max-w-3xl leading-relaxed">
            Manage live policy epoch cutovers, formulate candidate operational proposals using Amazon Bedrock Nova Lite reasoning, and execute Phase 2 read-after-write commit gating.
          </p>
        </div>

        <button
          onClick={loadPolicy}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-xl border border-zinc-800 bg-zinc-900 text-zinc-300 hover:text-white font-mono text-xs font-medium transition-colors self-start md:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh Authority</span>
        </button>
      </div>

      {backendError && (
        <BackendUnavailableBanner
          error={backendError}
          onRetry={loadPolicy}
          isRetrying={loading}
        />
      )}

      {/* Top Grid: Active Authority & In-Flight Cutover Publisher */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left: Active Authority Display */}
        <div className="lg:col-span-6 rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6 backdrop-blur-md">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-zinc-800">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-emerald-400" />
              <h3 className="font-bold text-white text-base">Active Authoritative Epoch</h3>
            </div>
            <span className="font-mono text-xs px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
              EPOCH G{activePolicy?.generation || 17}
            </span>
          </div>

          <div className="space-y-3 font-mono text-xs">
            <div className="flex justify-between py-1.5 border-b border-zinc-800/60">
              <span className="text-zinc-500">POLICY ID:</span>
              <span className="text-zinc-200">{activePolicy?.policy_id || "pol_commercial"}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-zinc-800/60">
              <span className="text-zinc-500">POLICY DIGEST:</span>
              <span className="text-emerald-300 truncate max-w-[280px]">
                {activePolicy?.policy_hash || "Computing..."}
              </span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-zinc-800/60">
              <span className="text-zinc-500">STORAGE BACKEND:</span>
              <span className="text-zinc-300">DynamoDB / SQLite WAL</span>
            </div>

            <div className="pt-2">
              <span className="text-zinc-500 block mb-2">ACTIVE TIER LIMITS:</span>
              <div className="grid grid-cols-2 gap-2">
                {(activePolicy?.rules || [
                  { client_tier: "standard", max_discount_amount: 500 },
                  { client_tier: "gold", max_discount_amount: 1000 },
                ]).map((r: any, i: number) => (
                  <div key={i} className="p-2 rounded bg-zinc-950 border border-zinc-800">
                    <span className="text-zinc-400 uppercase text-[10px] block">{r.client_tier} Tier</span>
                    <span className="text-white font-bold">${r.max_discount_amount} max</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right: Publish Next Cutover */}
        <div className="lg:col-span-6 rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6 backdrop-blur-md">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-zinc-800">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              <h3 className="font-bold text-white text-base">Publish Policy Cutover</h3>
            </div>
            <span className="font-mono text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
              ATOMIC CAS CUTOVER
            </span>
          </div>

          <div className="space-y-4 text-xs font-mono">
            <div>
              <label className="block text-zinc-400 mb-1">Target Epoch Generation:</label>
              <input
                type="number"
                value={cutoverTargetGen}
                onChange={(e) => setCutoverTargetGen(Number(e.target.value))}
                className="w-full p-2 bg-zinc-950 border border-zinc-800 rounded-lg text-white"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-zinc-400 mb-1">Standard Tier Limit ($):</label>
                <input
                  type="number"
                  value={cutoverStandardLimit}
                  onChange={(e) => setCutoverStandardLimit(Number(e.target.value))}
                  className="w-full p-2 bg-zinc-950 border border-zinc-800 rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-zinc-400 mb-1">Gold Tier Limit ($):</label>
                <input
                  type="number"
                  value={cutoverGoldLimit}
                  onChange={(e) => setCutoverGoldLimit(Number(e.target.value))}
                  className="w-full p-2 bg-zinc-950 border border-zinc-800 rounded-lg text-white"
                />
              </div>
            </div>

            <button
              onClick={handlePublishCutover}
              disabled={loading}
              className="w-full mt-2 py-2.5 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white font-bold rounded-lg transition-colors shadow-lg shadow-amber-950/40"
            >
              {loading ? "Publishing Cutover..." : `Execute Cutover to G${cutoverTargetGen}`}
            </button>
          </div>
        </div>
      </div>

      {/* Operational Request Execution Lifecycle */}
      <div className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6 backdrop-blur-md space-y-6">
        <div className="pb-4 border-b border-zinc-800 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-white">Consequential Request Lifecycle</h3>
            <p className="text-xs text-zinc-400 font-mono mt-0.5">
              Plane A Reasoning &rarr; Plane B Generation Fence &rarr; Plane B Read-After-Write CAS &rarr; Plane D Permit Execution
            </p>
          </div>
        </div>

        {/* Input Form */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs font-mono">
          <div>
            <label className="block text-zinc-400 mb-1">Client Tier:</label>
            <select
              value={clientTier}
              onChange={(e) => setClientTier(e.target.value)}
              className="w-full p-2.5 bg-zinc-950 border border-zinc-800 rounded-lg text-white"
            >
              <option value="standard">Standard</option>
              <option value="silver">Silver</option>
              <option value="gold">Gold</option>
              <option value="platinum">Platinum (Requires Escalation)</option>
            </select>
          </div>

          <div>
            <label className="block text-zinc-400 mb-1">Requested Discount ($):</label>
            <input
              type="number"
              value={discountAmount}
              onChange={(e) => setDiscountAmount(Number(e.target.value))}
              className="w-full p-2.5 bg-zinc-950 border border-zinc-800 rounded-lg text-white"
            />
          </div>

          <div>
            <label className="block text-zinc-400 mb-1">Invoice ID:</label>
            <input
              type="text"
              value={invoiceId}
              onChange={(e) => setInvoiceId(e.target.value)}
              className="w-full p-2.5 bg-zinc-950 border border-zinc-800 rounded-lg text-white"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={handleEvaluateRequest}
              disabled={evaluating}
              className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold rounded-lg transition-colors shadow-lg shadow-emerald-950/40"
            >
              {evaluating ? "Reasoning with Bedrock..." : "Step 1: Evaluate Proposal"}
            </button>
          </div>
        </div>

        {/* Results Progression Display */}
        {evalResult && (
          <div className="pt-4 border-t border-zinc-800 space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Proposal & Fence Result */}
              <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-950 font-mono text-xs space-y-2">
                <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
                  <span className="text-zinc-400">PLANE A REASONING & PROPOSAL</span>
                  <span
                    className={`font-bold px-2 py-0.5 rounded ${
                      evalResult.allowed
                        ? "bg-emerald-500/20 text-emerald-300"
                        : "bg-rose-500/20 text-rose-300"
                    }`}
                  >
                    {evalResult.status}
                  </span>
                </div>
                <p className="text-zinc-300 font-sans text-xs pt-1">
                  <strong>Rationale:</strong> {evalResult.proposal?.rationale || evalResult.reason}
                </p>
                <div className="text-[11px] text-zinc-400 pt-2 space-y-1">
                  <p>Proposed Epoch: G{evalResult.proposed_generation}</p>
                  <p>Visible Authority Epoch: G{evalResult.current_generation}</p>
                  {evalResult.receipt && (
                    <p className="text-emerald-400 truncate">
                      Receipt ID: {evalResult.receipt.receipt_id}
                    </p>
                  )}
                </div>
              </div>

              {/* Phase 2 Commit Action */}
              <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-950 font-mono text-xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
                    <span className="text-zinc-400">PLANE B TWO-PHASE COMMIT GATE</span>
                    <span className="text-zinc-500">Read-After-Write CAS</span>
                  </div>
                  <p className="text-zinc-400 text-xs mt-2">
                    Phase 2 validates that active policy authority has not advanced between proposal issuance and commit.
                  </p>
                </div>

                <div className="pt-4">
                  <button
                    onClick={handleCommitRequest}
                    disabled={committing || !evalResult.receipt}
                    className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-bold rounded-lg transition-colors shadow-lg shadow-blue-950/40"
                  >
                    {committing ? "Verifying CAS Gate..." : "Step 2: Commit Gate (Phase 2)"}
                  </button>
                </div>
              </div>
            </div>

            {/* Commit Outcome */}
            {commitResult && (
              <div
                className={`p-4 rounded-xl border font-mono text-xs ${
                  commitResult.committed
                    ? "border-emerald-500/40 bg-emerald-950/20 text-emerald-200"
                    : "border-rose-500/40 bg-rose-950/20 text-rose-200"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm">
                    {commitResult.committed
                      ? "COMMITTED: Execution Permit Issued"
                      : `ABORTED: ${commitResult.status}`}
                  </span>
                  <span className="text-xs font-mono">{commitResult.status}</span>
                </div>
                {commitResult.error && (
                  <p className="text-rose-300 mt-2 font-sans">{commitResult.error}</p>
                )}
                {commitResult.permit && (
                  <div className="mt-2 pt-2 border-t border-emerald-500/20 text-[11px] space-y-0.5">
                    <p>Permit ID: {commitResult.permit.permit_id}</p>
                    <p>Kernel Signature: {commitResult.permit.kernel_signature.slice(0, 24)}...</p>
                    <p>Generation Bound: G{commitResult.permit.policy_generation}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
