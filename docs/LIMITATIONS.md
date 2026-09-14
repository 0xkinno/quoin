# QUOIN Scope, Boundaries & Limitations

Honest engineering requires making system boundaries and assumptions explicit:

## 1. Scope of Enforced Invariants
- **Operational Policy Scope:** QUOIN is designed for operational workflows (pricing, discounts, credits, deadlines, contract terms) with quantifiable parameters.
- **Natural Language Subjectivity:** Qualitative guidelines (e.g. "be polite", "represent the brand warmly") remain the responsibility of prompt engineering; QUOIN enforces mathematical boundaries, generation freshness, and quantitative ceilings.

## 2. Infrastructure Latency Assumptions
- **Visibility Delay:** QUOIN assumes memory consolidation operates with positive lag ($\Delta t > 0$). In instantaneous synchronous stores, the generation fence remains active with zero penalty.
- **Clock Drift:** Receipt expiration relies on standard NTP synchronization (within $\pm 100\text{ms}$).

## 3. Human Escalation Path
- QUOIN is not an automated negotiation bot. When an action is blocked due to policy mismatch or ceiling violation, QUOIN aborts the commit and re-evaluates or escalates to human operational leads.
