import type { Metadata } from "next";
import "./globals.css";
import { PremiumNav } from "@/components/PremiumNav";

export const metadata: Metadata = {
  title: "QUOIN — Deterministic Policy-Generation Fence for Autonomous Agents",
  description: "Accepted is not the same as visible. Eliminating in-flight cutover races across four strictly isolated architectural planes.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen flex flex-col antialiased bg-[var(--bg)] text-[var(--t2)] selection:bg-[var(--rec)] selection:text-white transition-colors duration-200">
        <PremiumNav />
        <main className="flex-1">{children}</main>
        <footer className="border-t border-[var(--line)] py-8 text-center text-xs font-mono text-[var(--t3)] bg-[var(--bg2)] transition-colors duration-200">
          <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
            <div>QUOIN &middot; Deterministic Policy-Generation Fence &middot; 4-Plane Architecture</div>
            <div className="flex items-center gap-4 text-[var(--t3)]">
              <span>Plane A: Bedrock / Strands</span>
              <span>&bull;</span>
              <span>Plane B: Deterministic Kernel</span>
              <span>&bull;</span>
              <span>Plane C: AgentCore Memory</span>
              <span>&bull;</span>
              <span>Plane D: Execution Permits</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
