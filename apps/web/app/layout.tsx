import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "QUOIN — Policy-Generation Fence for Professional Agents",
  description: "Accepted is not the same as visible. Fencing agent actions to verified policy authority.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col antialiased">
        <Navbar />
        <main className="flex-1">{children}</main>
        <footer className="border-t border-paper-200 py-8 text-center text-xs font-mono text-graphite-subtle bg-paper-100">
          <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
            <div>QUOIN &middot; AWS Agents for Humans 2026 &middot; Professional Agents Track</div>
            <div className="flex items-center gap-4">
              <span>Pure Python Kernel</span>
              <span>&bull;</span>
              <span>AWS AgentCore Memory</span>
              <span>&bull;</span>
              <span>Strands Agents</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
