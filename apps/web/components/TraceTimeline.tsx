"use client";

import React, { useState, useEffect } from "react";
import { GitCommit, ShieldCheck, ShieldAlert, CheckCircle2, Copy, Search, RefreshCw, ChevronDown, ChevronRight, Lock } from "lucide-react";
import { api, BackendUnavailableError } from "@/lib/api";
import { BackendUnavailableBanner } from "./BackendUnavailableBanner";

export const TraceTimeline: React.FC = () => {
  const [requestId, setRequestId] = useState("req_sample_fenced_01");
  const [traceData, setTraceData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [backendError, setBackendError] = useState<string | null>(null);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [verificationResult, setVerificationResult] = useState<any>(null);
  const [verifying, setVerifying] = useState(false);
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  const fetchTrace = async (id: string) => {
    setLoading(true);
    setBackendError(null);
    setVerificationResult(null);
    try {
      const res = await api.getTrace(id);
      setTraceData(res);
      setVerificationResult(res.verification);
    } catch (err: any) {
      if (err instanceof BackendUnavailableError) {
        setBackendError(err.message);
      } else {
        setBackendError(err.message || "Failed to load decision trace.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrace(requestId);
  }, []);

  const handleVerifyChain = async () => {
    if (!traceData?.events) return;
    setVerifying(true);
    try {
      const res = await api.verifyTrace({
        request_id: traceData.request_id,
        events: traceData.events,
      });
      setVerificationResult(res);
    } catch (err: any) {
      alert("Verification call failed: " + err.message);
    } finally {
      setVerifying(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedHash(text);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  const toggleExpand = (idx: number) => {
    setExpandedIndex(expandedIndex === idx ? null : idx);
  };

  return (
    <div className="w-full space-y-6">
      {backendError && (
        <BackendUnavailableBanner
          error={backendError}
          onRetry={() => fetchTrace(requestId)}
          isRetrying={loading}
        />
      )}

      {/* Search & Actions Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl border border-zinc-800 bg-zinc-900/60 backdrop-blur-md">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-80">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={requestId}
              onChange={(e) => setRequestId(e.target.value)}
              placeholder="Enter Request ID..."
              className="w-full pl-9 pr-3 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-sm text-zinc-200 font-mono focus:outline-none focus:border-emerald-500"
            />
          </div>
          <button
            onClick={() => fetchTrace(requestId)}
            disabled={loading}
            className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg text-sm font-medium transition-colors shrink-0"
          >
            {loading ? "Loading..." : "Load Trace"}
          </button>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
          <button
            onClick={() => {
              setRequestId("req_sample_fenced_01");
              fetchTrace("req_sample_fenced_01");
            }}
            className="text-xs text-zinc-400 hover:text-emerald-400 underline font-mono"
          >
            Load Verified Sample Trace
          </button>
          <button
            onClick={handleVerifyChain}
            disabled={verifying || !traceData?.events}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-lg text-sm font-semibold transition-all shadow-lg shadow-emerald-950/40 shrink-0"
          >
            <ShieldCheck className={`w-4 h-4 ${verifying ? "animate-spin" : ""}`} />
            <span>{verifying ? "Verifying..." : "Verify Hash Chain"}</span>
          </button>
        </div>
      </div>

      {/* Verification Status Banner */}
      {verificationResult && (
        <div
          className={`p-4 rounded-xl border flex items-center justify-between gap-4 font-mono text-xs ${
            verificationResult.valid || verificationResult.status === "TRACE_INTACT" || verificationResult.status === "TRACE INTACT"
              ? "border-emerald-500/40 bg-emerald-950/20 text-emerald-300"
              : "border-rose-500/40 bg-rose-950/20 text-rose-300"
          }`}
        >
          <div className="flex items-center gap-3">
            {verificationResult.valid || verificationResult.status === "TRACE_INTACT" || verificationResult.status === "TRACE INTACT" ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            ) : (
              <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0" />
            )}
            <div>
              <p className="font-bold text-sm">
                STATUS: {verificationResult.status || (verificationResult.valid ? "TRACE INTACT" : "TRACE ALTERED")}
              </p>
              <p className="text-[11px] opacity-80 mt-0.5">
                {verificationResult.details || `All events verified against canonical SHA-256 genesis binding.`}
              </p>
            </div>
          </div>
          {verificationResult.head_hash && (
            <div className="hidden md:flex items-center gap-2 text-[11px]">
              <span className="text-zinc-500">HEAD DIGEST:</span>
              <span className="text-zinc-200">{verificationResult.head_hash.slice(0, 16)}...</span>
            </div>
          )}
        </div>
      )}

      {/* Timeline Events List */}
      {traceData?.events && traceData.events.length > 0 ? (
        <div className="relative pl-6 border-l-2 border-zinc-800 space-y-8 my-8 ml-4">
          {traceData.events.map((ev: any, idx: number) => {
            const isExpanded = expandedIndex === idx;
            return (
              <div key={ev.sequence_index || idx} className="relative group">
                {/* Node icon */}
                <div className="absolute -left-[35px] top-1 w-6 h-6 rounded-full bg-zinc-950 border-2 border-emerald-500 flex items-center justify-center text-emerald-400 text-xs font-mono font-bold shadow-md shadow-emerald-950">
                  {ev.sequence_index}
                </div>

                <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-5 hover:border-zinc-700 transition-all backdrop-blur-md">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {ev.event_type}
                      </span>
                      <span className="text-xs text-zinc-400 font-mono">{ev.timestamp}</span>
                    </div>

                    <button
                      onClick={() => toggleExpand(idx)}
                      className="flex items-center gap-1 text-xs text-zinc-400 hover:text-white transition-colors self-start sm:self-auto"
                    >
                      {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                      <span>{isExpanded ? "Collapse Payload" : "Inspect Payload"}</span>
                    </button>
                  </div>

                  {/* Cryptographic Linkage Info */}
                  <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] font-mono">
                    <div className="p-2 rounded bg-zinc-950/80 border border-zinc-800/80 flex items-center justify-between">
                      <div className="truncate mr-2">
                        <span className="text-zinc-500">PREV: </span>
                        <span className="text-zinc-300">{ev.previous_hash}</span>
                      </div>
                      <button
                        onClick={() => copyToClipboard(ev.previous_hash)}
                        title="Copy Hash"
                        className="text-zinc-400 hover:text-white shrink-0"
                      >
                        <Copy className="w-3 h-3" />
                      </button>
                    </div>

                    <div className="p-2 rounded bg-zinc-950/80 border border-zinc-800/80 flex items-center justify-between">
                      <div className="truncate mr-2">
                        <span className="text-emerald-500">CURR: </span>
                        <span className="text-emerald-300 font-bold">{ev.current_hash}</span>
                      </div>
                      <button
                        onClick={() => copyToClipboard(ev.current_hash)}
                        title="Copy Hash"
                        className="text-zinc-400 hover:text-white shrink-0"
                      >
                        <Copy className="w-3 h-3" />
                      </button>
                    </div>
                  </div>

                  {/* Expandable JSON Payload */}
                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-zinc-800">
                      <p className="text-xs font-mono text-zinc-400 mb-2">CANONICAL PAYLOAD DATA:</p>
                      <pre className="p-3 rounded-lg bg-zinc-950 text-emerald-300/90 font-mono text-xs overflow-x-auto border border-zinc-800/80">
                        {JSON.stringify(ev.payload || ev, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        !loading &&
        !backendError && (
          <div className="p-12 text-center text-zinc-400 font-mono text-sm rounded-xl border border-zinc-800 bg-zinc-900/30">
            No events found for request ID &quot;{requestId}&quot;. Click &quot;Load Verified Sample Trace&quot; to inspect an authentic forensic chain.
          </div>
        )
      )}
    </div>
  );
};
