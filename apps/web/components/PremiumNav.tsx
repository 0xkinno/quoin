"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck, Terminal, Bug, GitCommit, FileCheck, ExternalLink, Activity } from "lucide-react";
import { api } from "@/lib/api";
import { ThemeToggle } from "./ThemeToggle";

export const PremiumNav: React.FC = () => {
  const pathname = usePathname();
  const [backendStatus, setBackendStatus] = useState<"ONLINE" | "OFFLINE" | "CHECKING">("CHECKING");
  const [activePlanes, setActivePlanes] = useState<number>(4);

  useEffect(() => {
    let mounted = true;
    api.getHealth()
      .then((res) => {
        if (mounted) {
          setBackendStatus(res.status === "HEALTHY" ? "ONLINE" : "OFFLINE");
          if (res.planes_active) setActivePlanes(res.planes_active.length);
        }
      })
      .catch(() => {
        if (mounted) setBackendStatus("OFFLINE");
      });
    return () => {
      mounted = false;
    };
  }, [pathname]);

  const navLinks = [
    { href: "/", label: "Overview", icon: ShieldCheck },
    { href: "/console", label: "Console", icon: Terminal },
    { href: "/lab", label: "Break It Lab (27)", icon: Bug },
    { href: "/trace", label: "Decision Trace", icon: GitCommit },
    { href: "/proof", label: "Proof Center", icon: FileCheck },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-[var(--line)] bg-[var(--bg)]/85 backdrop-blur-xl transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-white font-mono font-bold shadow-lg shadow-emerald-900/30 group-hover:scale-105 transition-transform">
              Q
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold tracking-tight text-[var(--t1)] font-mono text-base">QUOIN</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded border border-emerald-500/30 bg-emerald-500/10 text-emerald-500 font-semibold uppercase">
                  4-Plane Kernel
                </span>
              </div>
              <p className="text-[11px] text-[var(--t3)] hidden sm:block">
                Deterministic Policy Fence
              </p>
            </div>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-1 pl-4 border-l border-[var(--line)]">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? "bg-[var(--line2)] text-[var(--t1)] shadow-sm border border-[var(--line)]"
                      : "text-[var(--t2)] hover:text-[var(--t1)] hover:bg-[var(--shell)]"
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? "text-emerald-500" : "text-[var(--t3)]"}`} />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right Status & Controls */}
        <div className="flex items-center gap-3">
          {/* Backend Status Pill */}
          <div
            title={`Backend Service: ${backendStatus}`}
            className="flex items-center gap-2 px-2.5 py-1 rounded-full border border-[var(--line)] bg-[var(--bg2)]/80 text-xs font-mono"
          >
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus === "ONLINE"
                  ? "bg-emerald-500 shadow-sm shadow-emerald-500"
                  : backendStatus === "CHECKING"
                  ? "bg-amber-500 animate-pulse"
                  : "bg-red-500 animate-ping"
              }`}
            />
            <span className="text-[var(--t1)] hidden sm:inline font-medium">
              {backendStatus === "ONLINE" ? `KERNEL ACTIVE (${activePlanes}P)` : backendStatus}
            </span>
          </div>

          <ThemeToggle />

          <a
            href="https://github.com/0xkinno/quoin"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[var(--line)] bg-[var(--bg2)] hover:bg-[var(--shell)] text-xs font-mono text-[var(--t2)] hover:text-[var(--t1)] transition-colors"
          >
            <span>GitHub</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </header>
  );
};
