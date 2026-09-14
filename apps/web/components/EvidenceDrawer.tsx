"use client";

import React, { useState, useEffect } from "react";
import { FileText, Copy, Download, X, Check, Eye } from "lucide-react";
import { api, BackendUnavailableError } from "@/lib/api";

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export const EvidenceDrawer: React.FC<Props> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<"benchmark" | "attacks" | "memory" | "manifest">("benchmark");
  const [data, setData] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    setLoading(true);

    Promise.allSettled([
      api.getBenchmarkResults(),
      api.getAttackResults(),
      api.getMemoryVisibility(),
      api.getManifest(),
    ]).then(([bench, att, mem, man]) => {
      setData({
        benchmark: bench.status === "fulfilled" ? bench.value : { error: "Unavailable" },
        attacks: att.status === "fulfilled" ? att.value : { error: "Unavailable" },
        memory: mem.status === "fulfilled" ? mem.value : { error: "Unavailable" },
        manifest: man.status === "fulfilled" ? man.value : { error: "Unavailable" },
      });
      setLoading(false);
    });
  }, [isOpen]);

  if (!isOpen) return null;

  const currentContent = JSON.stringify(data[activeTab] || {}, null, 2);

  const copyContent = () => {
    navigator.clipboard.writeText(currentContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadFile = () => {
    const blob = new Blob([currentContent], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `quoin_${activeTab}_evidence.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 sm:p-6">
      <div className="relative w-full max-w-5xl h-[85vh] rounded-2xl border border-zinc-800 bg-zinc-950 flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-zinc-800">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Machine-Readable Evidence Vault</h3>
              <p className="text-xs text-zinc-400 font-mono">
                Cryptographically validated raw audit files and empirical data
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={copyContent}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-xs font-mono text-zinc-300 transition-colors"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? "Copied" : "Copy JSON"}</span>
            </button>
            <button
              onClick={downloadFile}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-xs font-mono text-zinc-300 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Tab Selector */}
        <div className="flex items-center gap-2 px-5 py-3 border-b border-zinc-800/80 bg-zinc-900/40 text-xs font-mono">
          {[
            { key: "benchmark", label: "benchmark/results.json" },
            { key: "attacks", label: "traces/attack_results.json" },
            { key: "memory", label: "aws/memory_visibility_summary.json" },
            { key: "manifest", label: "manifests/manifest.json" },
          ].map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key as any)}
              className={`px-3 py-1.5 rounded-md transition-colors ${
                activeTab === t.key
                  ? "bg-emerald-600 text-white font-semibold"
                  : "text-zinc-400 hover:text-white bg-zinc-900"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* JSON Viewer */}
        <div className="flex-1 p-5 overflow-auto bg-zinc-950 font-mono text-xs text-emerald-300/90 leading-relaxed">
          {loading ? (
            <div className="flex items-center justify-center h-full text-zinc-500">
              Loading evidence file...
            </div>
          ) : (
            <pre>{currentContent}</pre>
          )}
        </div>
      </div>
    </div>
  );
};
