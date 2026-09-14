"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";

export const Hero: React.FC = () => {
  return (
    <header className="relative z-1 min-h-[92vh] overflow-hidden flex flex-col justify-center border-b border-[var(--line)] bg-[var(--bg)] transition-colors duration-200">
      {/* Full-bleed hero visual with crisp clarity, shifted right to prevent clashing with action buttons */}
      <div className="absolute inset-0 z-0 flex justify-end">
        <Image
          src="/hero.jpg"
          alt="QUOIN Architectural Core"
          fill
          priority
          className="object-cover object-[86%_center] opacity-85 dark:opacity-80 transition-opacity"
        />
      </div>

      {/* Directional gradient mask on the left text area: ensures buttons and text have clean separation while the figure on the right is completely unobscured */}
      <div
        className="absolute inset-y-0 left-0 w-full lg:w-[55%] z-1 pointer-events-none bg-gradient-to-r from-[var(--bg)] via-[var(--bg)]/85 to-transparent transition-colors duration-200"
      />
      <div
        className="absolute inset-x-0 bottom-0 h-16 z-1 pointer-events-none bg-gradient-to-t from-[var(--bg)] to-transparent transition-colors duration-200"
      />

      {/* Hero Content Container */}
      <div className="relative z-2 max-w-[1400px] w-full mx-auto px-6 sm:px-10 lg:px-14 py-20 flex flex-col justify-center min-h-[92vh]">
        <div className="max-w-[42rem]">
          {/* Eyebrow Chip */}
          <div className="chip-eyebrow">
            <i />
            <span>
              AUTHORITATIVE CUTOVER <b>·</b> <b className="text-[var(--proof)]">EPOCH G18 ACTIVE</b>
            </span>
          </div>

          {/* Display Headline with Unbounded styling */}
          <h1 className="text-4xl sm:text-6xl lg:text-[4.2rem] font-extrabold tracking-tight text-[var(--t1)] leading-[1.04] mb-6">
            <span>Your agent executed on a </span>
            <span className="text-[var(--rec)]">stale policy?</span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-[var(--t2)] leading-relaxed mb-8 max-w-[34rem]">
            <b className="text-[var(--t1)] font-semibold">Causality before capital.</b> QUOIN fences in-flight cutover
            races, memory visibility lag, and unauthorized side effects with cryptographically bound Two-Phase Commit
            leases anchored on AWS DynamoDB &amp; Bedrock.
          </p>

          {/* Action CTAs using Replay .btn style */}
          <div className="flex flex-wrap items-center gap-4">
            <Link href="/console" className="btn primary">
              <span>Open Console</span>
              <span className="chip">↗</span>
            </Link>

            <a href="#scrub" className="btn">
              <span>Scrub Causal Trace</span>
              <span className="chip">↓</span>
            </a>

            <Link href="/lab" className="btn">
              <span>Run 27 Attacks</span>
              <span className="chip">→</span>
            </Link>
          </div>

          {/* Invariant Equation Strip */}
          <div className="mt-10 p-3.5 border border-[var(--line)] bg-[var(--bg2)]/80 backdrop-blur-sm max-w-xl flex items-center justify-between font-mono text-[0.72rem]">
            <span className="text-[var(--t3)] uppercase tracking-wider">Kernel Invariant:</span>
            <span className="text-[var(--proof)] font-medium tracking-tight">
              G_proposal ≡ G_visible = G_active ∧ H(P) = H_receipt
            </span>
          </div>
        </div>
      </div>

      {/* Hero Bottom-Right Run Signature */}
      <div className="hidden lg:flex absolute z-2 right-10 bottom-10 font-mono text-[0.64rem] tracking-[0.16em] uppercase text-[var(--t3)] text-right flex-col gap-1.5 bg-[var(--bg)]/80 backdrop-blur-md p-4 border border-[var(--line)]">
        <span>
          BENCHMARK <b className="text-[var(--t1)]">CAUSAL-100-SUITE</b>
        </span>
        <span>
          SCENARIOS <b className="text-[var(--t1)]">100 / 100</b> <b>·</b>{" "}
          <span className="text-[var(--proof)]">0 STALE EXECUTIONS</span>
        </span>
        <span>
          LEDGER <b className="text-[var(--t1)]">DYNAMODB CAS</b> <b>·</b>{" "}
          <span className="text-[var(--rec)]">G17 &rarr; G18 PROVEN</span>
        </span>
      </div>
    </header>
  );
};

