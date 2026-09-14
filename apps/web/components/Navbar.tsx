"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck, Terminal, Cpu, CheckCircle2 } from "lucide-react";

export function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Overview", href: "/" },
    { name: "Cutover Console", href: "/console" },
    { name: "Break It Lab", href: "/lab" },
    { name: "Proof Center", href: "/proof" },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#F9F9FB]/90 backdrop-blur-md border-b border-paper-200">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded bg-graphite-main flex items-center justify-center text-white font-mono font-bold text-sm tracking-tighter">
            Q
          </div>
          <div className="flex flex-col">
            <span className="font-bold tracking-tight text-graphite-main text-base leading-none">QUOIN</span>
            <span className="text-[10px] font-mono text-graphite-subtle uppercase tracking-wider mt-0.5">Policy Generation Fence</span>
          </div>
        </Link>

        {/* Navigation links */}
        <nav className="hidden md:flex items-center gap-1 bg-paper-100 p-1 rounded-lg border border-paper-200">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3.5 py-1.5 rounded-md text-xs font-medium transition-all ${
                  isActive
                    ? "bg-white text-graphite-main shadow-sm font-semibold"
                    : "text-graphite-muted hover:text-graphite-main hover:bg-white/50"
                }`}
              >
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Live Authority Status Badge */}
        <div className="flex items-center gap-2.5 text-xs font-mono bg-emerald-50 text-emerald-700 border border-emerald-200 px-3 py-1.5 rounded-full">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="font-medium">FENCE ACTIVE (G17/G18)</span>
        </div>
      </div>
    </header>
  );
}
