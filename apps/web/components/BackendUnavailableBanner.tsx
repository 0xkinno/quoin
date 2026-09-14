"use client";

import React from "react";
import { AlertTriangle, RefreshCw, ServerOff } from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

interface Props {
  onRetry?: () => void;
  isRetrying?: boolean;
  error?: string;
}

export const BackendUnavailableBanner: React.FC<Props> = ({
  onRetry,
  isRetrying = false,
  error,
}) => {
  return (
    <div className="my-6 rounded-xl border border-red-500/40 bg-red-950/20 p-6 text-red-200 backdrop-blur-md shadow-2xl">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-red-500/10 rounded-lg text-red-400 border border-red-500/20">
            <ServerOff className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs uppercase px-2 py-0.5 rounded bg-red-500/20 text-red-300 font-semibold tracking-wider">
                BACKEND UNAVAILABLE
              </span>
              <span className="text-xs text-zinc-400 font-mono">Target: {API_BASE_URL}</span>
            </div>
            <h3 className="text-lg font-bold text-white mt-1">
              Unable to Connect to QUOIN Kernel Service
            </h3>
            <p className="text-sm text-zinc-300 mt-1 max-w-2xl">
              {error ||
                `The FastAPI backend service is not responding at ${API_BASE_URL}. QUOIN strictly prohibits mock/simulated fallback data in production UI.`}
            </p>
          </div>
        </div>

        {onRetry && (
          <button
            onClick={onRetry}
            disabled={isRetrying}
            className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-red-600 hover:bg-red-500 text-white font-medium text-sm transition-all shadow-lg hover:shadow-red-500/25 disabled:opacity-50 shrink-0"
          >
            <RefreshCw className={`w-4 h-4 ${isRetrying ? "animate-spin" : ""}`} />
            <span>{isRetrying ? "Checking Connection..." : "Retry Connection"}</span>
          </button>
        )}
      </div>
    </div>
  );
};
