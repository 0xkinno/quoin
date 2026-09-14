"use client";

import { useState, useEffect } from "react";
import { Shield, ShieldAlert, CheckCircle2, RefreshCw, Lock, Zap, ArrowRight, FileCode, Check, AlertCircle } from "lucide-react";

export default function ConsolePage() {
  const [activePolicy, setActivePolicy] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [clientTier, setClientTier] = useState("gold");
  const [discountAmount, setDiscountAmount] = useState(700);
  const [requestResult, setRequestResult] = useState<any>(null);
  const [commitResult, setCommitResult] = useState<any>(null);
  const [evidenceDrawerOpen, setEvidenceDrawerOpen] = useState(false);

  // Fetch active policy
  const fetchPolicy = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/policies");
      if (res.ok) {
        const data = await res.json();
        setActivePolicy(data);
      } else {
        // Fallback default
        setActivePolicy({
          generation: 17,
          policy_id: "pol_agency_commercial_v1",
          policy_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          visible_at: new Date().toISOString(),
          rules: [
            { client_tier: "standard", max_discount_amount: 500.0, max_discount_percentage: 10.0 },
            { client_tier: "gold", max_discount_amount: 1500.0, max_discount_percentage: 20.0 }
          ]
        });
      }
    } catch {
      setActivePolicy({
        generation: 17,
        policy_id: "pol_agency_commercial_v1",
        policy_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        visible_at: new Date().toISOString(),
        rules: [
          { client_tier: "standard", max_discount_amount: 500.0, max_discount_percentage: 10.0 },
          { client_tier: "gold", max_discount_amount: 1500.0, max_discount_percentage: 20.0 }
        ]
      });
    }
  };

  useEffect(() => {
    fetchPolicy();
  }, []);

  // Trigger Cutover (e.g. G17 -> G18)
  const handleCutover = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/policies/cutover", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          max_gold_discount: 500.0, // Tightened from 1500 to 500!
          max_standard_discount: 300.0,
          visibility_lag_seconds: 0.1
        })
      });
      if (res.ok) {
        await fetch("http://localhost:8000/api/policies/force_sync", { method: "POST" });
        await fetchPolicy();
      }
    } catch (err) {
      // Local UI state transition if offline
      if (activePolicy) {
        setActivePolicy({
          ...activePolicy,
          generation: activePolicy.generation + 1,
          rules: [
            { client_tier: "standard", max_discount_amount: 300.0 },
            { client_tier: "gold", max_discount_amount: 500.0 }
          ]
        });
      }
    }
    setLoading(false);
  };

  // Reset to G17
  const handleReset = async () => {
    setLoading(true);
    try {
      await fetch("http://localhost:8000/api/policies/reset", { method: "POST" });
      await fetchPolicy();
    } catch {
      setActivePolicy({
        generation: 17,
        policy_id: "pol_agency_commercial_v1",
        policy_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        visible_at: new Date().toISOString(),
        rules: [
          { client_tier: "standard", max_discount_amount: 500.0 },
          { client_tier: "gold", max_discount_amount: 1500.0 }
        ]
      });
    }
    setRequestResult(null);
    setCommitResult(null);
    setLoading(false);
  };

  // Phase 1: Evaluate
  const handleEvaluate = async () => {
    setLoading(true);
    const payload = {
      request_id: `req_${Date.now().toString().slice(-4)}`,
      client_id: "cust_acme",
      client_tier: clientTier,
      amount: discountAmount,
      action: "apply_discount",
      invoice_id: "inv_409",
      discount_percentage: 14.0
    };

    try {
      const res = await fetch("http://localhost:8000/api/requests/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        setRequestResult({ ...data, rawPayload: payload });
        setCommitResult(null);
      }
    } catch {
      // Local fallback logic
      const currentGen = activePolicy?.generation || 17;
      const limit = clientTier === "gold" ? (currentGen >= 18 ? 500.0 : 1500.0) : 500.0;
      const allowed = discountAmount <= limit;
      setRequestResult({
        allowed,
        status: allowed ? "PERMITTED" : "POLICY_VIOLATION",
        reason: allowed ? `Fenced to Generation G${currentGen}` : `Discount $${discountAmount} exceeds $${limit} limit under G${currentGen}.`,
        current_generation: currentGen,
        proposed_generation: currentGen,
        proposal: {
          request_id: payload.request_id,
          requested_action: "apply_discount",
          requested_value: discountAmount,
          candidate_policy_generation: currentGen
        },
        receipt: allowed ? {
          receipt_id: `rcpt_${Math.random().toString(36).slice(2, 10)}`,
          policy_generation: currentGen,
          policy_hash: activePolicy?.policy_hash,
          issued_at: new Date().toISOString(),
          expires_at: new Date(Date.now() + 60000).toISOString()
        } : null,
        rawPayload: payload
      });
    }
    setLoading(false);
  };

  // Phase 2: Commit
  const handleCommit = async () => {
    if (!requestResult?.receipt) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/requests/commit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          receipt: requestResult.receipt,
          request_payload: requestResult.rawPayload,
          proposal: requestResult.proposal
        })
      });
      if (res.ok) {
        const data = await res.json();
        setCommitResult(data);
      }
    } catch {
      // Local fallback
      setCommitResult({
        committed: true,
        status: "COMMITTED",
        permit: {
          permit_id: `prmt_${Math.random().toString(36).slice(2, 10)}`,
          policy_generation: requestResult.current_generation,
          issued_at: new Date().toISOString()
        },
        effect_result: {
          status: "SUCCESS",
          discount_amount: discountAmount,
          committed_at: new Date().toISOString()
        }
      });
    }
    setLoading(false);
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-12 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-paper-200 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-graphite-main">Policy Cutover Console</h1>
          <p className="text-xs font-mono text-graphite-muted mt-1">
            Real-time in-flight policy race detection &amp; generation-fenced commit control
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleCutover}
            disabled={loading}
            className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-xs font-medium flex items-center gap-1.5 transition-all shadow-sm"
          >
            <Zap className="w-3.5 h-3.5" /> Promulgate G18 Cutover (Limit $500)
          </button>
          <button
            onClick={handleReset}
            disabled={loading}
            className="px-3 py-2 rounded-lg bg-paper-100 hover:bg-paper-200 text-graphite-main text-xs font-medium flex items-center gap-1.5 transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Reset (G17)
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Column 1: Live Request Intake */}
        <div className="p-6 rounded-2xl bg-white border border-paper-200 shadow-sm space-y-6">
          <div className="flex items-center justify-between border-b border-paper-200 pb-3">
            <h2 className="text-sm font-bold text-graphite-main uppercase tracking-wider font-mono">01. Request Intake</h2>
            <span className="text-[10px] font-mono bg-paper-100 px-2 py-0.5 rounded text-graphite-subtle">IN-FLIGHT</span>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-xs font-medium text-graphite-muted block mb-1">Client Tier</label>
              <select
                value={clientTier}
                onChange={(e) => setClientTier(e.target.value)}
                className="w-full text-xs font-mono p-2.5 rounded-lg border border-paper-200 bg-paper-50 focus:outline-none focus:ring-1 focus:ring-graphite-main"
              >
                <option value="standard">Standard Tier</option>
                <option value="silver">Silver Tier</option>
                <option value="gold">Gold Tier (High Value)</option>
                <option value="platinum">Platinum Tier (Executive)</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-medium text-graphite-muted block mb-1">Requested Discount ($)</label>
              <input
                type="number"
                value={discountAmount}
                onChange={(e) => setDiscountAmount(Number(e.target.value))}
                className="w-full text-xs font-mono p-2.5 rounded-lg border border-paper-200 bg-paper-50 focus:outline-none focus:ring-1 focus:ring-graphite-main"
              />
              <span className="text-[10px] text-graphite-subtle mt-1 block">
                Default: $700 (Valid under G17 limit $1500, but illegal under G18 limit $500)
              </span>
            </div>

            <button
              onClick={handleEvaluate}
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-graphite-main hover:bg-black text-white text-xs font-medium flex items-center justify-center gap-2 transition-all"
            >
              <Shield className="w-3.5 h-3.5" /> Step 1: Reason &amp; Evaluate Fence
            </button>
          </div>
        </div>

        {/* Column 2: Active Authority Memory */}
        <div className="p-6 rounded-2xl bg-white border border-paper-200 shadow-sm space-y-6">
          <div className="flex items-center justify-between border-b border-paper-200 pb-3">
            <h2 className="text-sm font-bold text-graphite-main uppercase tracking-wider font-mono">02. Active Authority</h2>
            <span className="text-[10px] font-mono bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">
              VISIBLE IN MEMORY
            </span>
          </div>

          <div className="space-y-4 text-xs font-mono">
            <div className="p-4 rounded-xl bg-paper-50 border border-paper-200 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-graphite-muted">Policy Generation:</span>
                <span className="font-bold text-sm text-graphite-main">G{activePolicy?.generation || 17}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-graphite-muted">Gold Discount Ceiling:</span>
                <span className="font-bold text-graphite-main">
                  ${activePolicy?.rules?.find((r: any) => r.client_tier === "gold")?.max_discount_amount || 1500.0}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-graphite-muted">Standard Ceiling:</span>
                <span className="font-bold text-graphite-main">
                  ${activePolicy?.rules?.find((r: any) => r.client_tier === "standard")?.max_discount_amount || 500.0}
                </span>
              </div>
            </div>

            <div className="space-y-1">
              <span className="text-[10px] text-graphite-subtle block">Canonical Policy Hash:</span>
              <div className="p-2 rounded bg-paper-100 text-[10px] text-graphite-muted break-all font-mono">
                {activePolicy?.policy_hash || "Computing digest..."}
              </div>
            </div>
          </div>
        </div>

        {/* Column 3: Generation Fence Gate & Commit */}
        <div className="p-6 rounded-2xl bg-white border border-paper-200 shadow-sm space-y-6">
          <div className="flex items-center justify-between border-b border-paper-200 pb-3">
            <h2 className="text-sm font-bold text-graphite-main uppercase tracking-wider font-mono">03. Fence Gate</h2>
            <span className="text-[10px] font-mono bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-bold">
              PHASE 2 CAS GATE
            </span>
          </div>

          {requestResult ? (
            <div className="space-y-4">
              <div className={`p-4 rounded-xl border ${
                requestResult.allowed
                  ? "bg-emerald-50/70 border-emerald-200 text-emerald-900"
                  : "bg-rose-50/70 border-rose-200 text-rose-900"
              }`}>
                <div className="flex items-center gap-2 font-bold text-xs">
                  {requestResult.allowed ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <ShieldAlert className="w-4 h-4 text-rose-600" />}
                  {requestResult.status}
                </div>
                <p className="text-[11px] mt-1.5 leading-relaxed">{requestResult.reason}</p>
                {requestResult.receipt && (
                  <div className="text-[10px] font-mono mt-2 pt-2 border-t border-emerald-200 text-emerald-700">
                    Receipt ID: {requestResult.receipt.receipt_id} (G{requestResult.receipt.policy_generation})
                  </div>
                )}
              </div>

              {requestResult.allowed && (
                <button
                  onClick={handleCommit}
                  disabled={loading || !!commitResult}
                  className="w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow"
                >
                  <Lock className="w-3.5 h-3.5" /> Step 2: Execute Phase 2 Commit
                </button>
              )}

              {commitResult && (
                <div className={`p-4 rounded-xl border text-xs font-mono ${
                  commitResult.committed
                    ? "bg-paper-50 border-paper-200 text-graphite-main"
                    : "bg-rose-50 border-rose-200 text-rose-900"
                }`}>
                  <div className="font-bold flex items-center gap-1.5">
                    {commitResult.committed ? <Check className="w-4 h-4 text-emerald-600" /> : <AlertCircle className="w-4 h-4 text-rose-600" />}
                    {commitResult.status}
                  </div>
                  {commitResult.error && <p className="text-[10px] text-rose-700 mt-1">{commitResult.error}</p>}
                  {commitResult.permit && (
                    <div className="text-[10px] text-graphite-muted mt-2 space-y-1">
                      <div>Permit: {commitResult.permit.permit_id}</div>
                      <div>Committed under: G{commitResult.permit.policy_generation}</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12 text-graphite-subtle text-xs font-mono">
              Awaiting Request Evaluation...
            </div>
          )}
        </div>
      </div>

      {/* Evidence Drawer Toggle */}
      <div className="pt-4 border-t border-paper-200">
        <button
          onClick={() => setEvidenceDrawerOpen(!evidenceDrawerOpen)}
          className="text-xs font-mono text-graphite-muted hover:text-graphite-main flex items-center gap-1.5 transition-all"
        >
          <FileCode className="w-4 h-4" /> {evidenceDrawerOpen ? "Hide Cryptographic Evidence Drawer" : "View Cryptographic Evidence Drawer"}
        </button>

        {evidenceDrawerOpen && (
          <div className="mt-4 p-6 rounded-2xl bg-paper-900 text-paper-100 font-mono text-xs space-y-4 overflow-x-auto shadow-inner">
            <div className="text-paper-300 font-bold uppercase tracking-wider text-[10px]">Verifiable Authority Receipts &amp; Audit Trail</div>
            <pre className="text-[11px] text-paper-200">
              {JSON.stringify({ activePolicy, requestResult, commitResult }, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
