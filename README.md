# QUOIN

[![Pytest Suite](https://img.shields.io/badge/pytest-31%2F31%20passed-emerald)](tests/)
[![Adversarial Break Suite](https://img.shields.io/badge/adversarial%20suite-27%2F27%20neutralized-blue)](docs/THREAT_MODEL.md)
[![Causal Benchmark](https://img.shields.io/badge/causal%20benchmark-100%2F100%20scenarios-purple)](benchmarks/)
[![Stale Executions](https://img.shields.io/badge/stale%20executions-0%20escapes-brightgreen)](evidence/benchmark/results.json)
[![Authoritative Ledger](https://img.shields.io/badge/authority%20ledger-DynamoDB%202PC-amber)](quoin/authority/)
[![Reasoning Agent](https://img.shields.io/badge/Strands%20SDK-Amazon%20Bedrock%20Nova%20Lite-orange)](quoin/agent/)
[![Master Verifier](https://img.shields.io/badge/master%20verifier-10%2F10%20passed%20(100%25)-teal)](scripts/verify_all.py)
[![License](https://img.shields.io/badge/license-Apache%202.0-slate)](LICENSE)

---

<p align="center">
  <img src="docs/assets/quoin-banner.png" alt="QUOIN Platform Banner" width="100%" />
</p>

> **Accepted is not the same as visible.**  
> QUOIN prevents autonomous agents from committing unauthorized operational side effects during policy cutover races by enforcing a model-free, deterministic two-phase commit fence anchored to monotonic generation receipts and DynamoDB CAS gates.

---

## Product Links

| Resource | Link | Description |
| :--- | :--- | :--- |
| **Interactive Web Application** | [quoin.vercel.app](https://quoin.vercel.app) *(Deployment pending)* | Next.js 14 editorial web application with Replay design aesthetic, scrub timeline, and operator console |
| **Video Demonstration** | [YouTube Walkthrough](https://www.youtube.com/watch?v=placeholder) | Complete end-to-end technical walkthrough and live failure demonstration |
| **FastAPI Backend Service** | [quoin-api.onrender.com](https://quoin-api.onrender.com) *(Deployment pending)* | Pure Python deterministic authority fence, DynamoDB CAS cutover gate, and Bedrock Nova Lite bridge |
| **GitHub Repository** | [github.com/0xkinno/quoin](https://github.com/0xkinno/quoin) | Primary open-source codebase, test suites, and empirical evidence manifests |

---

## Product Interfaces

<table>
  <tr>
    <td width="50%">
      <img src="evidence/screenshots/landing_Desktop_Standard__1280px_.png" alt="QUOIN Landing Interface" />
      <p align="center"><b>Figure 1: Editorial Landing & Causal Scrub Timeline</b></p>
    </td>
    <td width="50%">
      <img src="evidence/screenshots/console_desktop.png" alt="Operator Console" />
      <p align="center"><b>Figure 2: Operator Console & 2PC Lease Issuance</b></p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <img src="evidence/screenshots/lab_attacks_desktop.png" alt="Break It Lab" />
      <p align="center"><b>Figure 3: Break It Lab (27 Adversarial Attacks)</b></p>
    </td>
    <td width="50%">
      <img src="evidence/screenshots/trace_timeline_desktop.png" alt="Decision Trace Timeline" />
      <p align="center"><b>Figure 4: Decision Trace Forensic Merkle Timeline</b></p>
    </td>
  </tr>
</table>

---

## Operational Rationale & Consistency Invariant

When an enterprise updates a business rule, such as lowering the maximum allowable commercial discount from 20% to 10%, the update acknowledges immediately at the ingest API. However, memory propagation and index consolidation in distributed agent backends require asynchronous processing time. 

During this gap, an in-flight autonomous agent queries memory, retrieves the superseded 20% discount policy, reasons that a 15% discount is permissible, and commits a transaction that destroys operating margin.

**QUOIN eliminates this failure mode entirely.** It inserts a model-free deterministic fence between the reasoning agent and side-effect execution. If the policy generation observed during reasoning differs from the authoritative active generation at the commit gate, the transaction is rejected instantly before any financial side effect occurs.

---

## The Problem

Modern enterprises increasingly delegate high-consequence operations to autonomous generative agents: issuing commercial credits, adjusting contract terms, approving invoice discounts, and waiving SLA penalties.

In these systems, policy updates are frequent and asynchronous:
1. **The In-Flight Cutover Race:** An agent starts a multi-step reasoning workflow at $T_0$ under Policy Generation $G_{17}$. At $T_1$, an executive committee publishes Policy Generation $G_{18}$. At $T_2$, the agent emits a side-effect command valid under $G_{17}$ but illegal under $G_{18}$.
2. **The Memory Visibility Lag:** Even after write acknowledgement (`HTTP 200`), distributed vector stores and semantic memory tiers exhibit replication latency ($T_{\text{visibility}}$) before records become retrievable.
3. **The Confabulated Authority Trap:** Generative models cannot self-police authority. A prompt injection or poisoned retrieval context can induce an LLM to claim it possesses approval privileges it was never granted.

Without an external, model-free deterministic fence, eventual consistency produces unrecoverable real-world financial damage.

---

## System Architecture

<p align="center">
  <img src="docs/assets/quoin-architecture.png" alt="QUOIN Four-Plane Architecture" width="100%" />
</p>

QUOIN isolates responsibilities into four distinct architectural planes:
- **Plane A (Cognitive Reasoning):** Amazon Bedrock Nova Lite via Strands Agents SDK. Parses user prompts, queries context, and generates structured `DecisionProposal` objects. Strictly unprivileged; zero direct tool execution credentials.
- **Plane B (Deterministic Kernel Fence):** Pure Python / Rust hasher. Evaluates proposals against generation-scoped policy rules, computes SHA-256 Merkle bindings, and enforces mathematical boundary conditions.
- **Plane C (Cognitive Memory & Authoritative Ledger):** Dual-tier storage. Amazon Bedrock AgentCore Memory provides episodic context; Amazon DynamoDB provides linearizable, conditional-write policy cutover epochs and 2PC leases.
- **Plane D (Operational Action Service):** Idempotent transaction execution. Validates single-use permits, verifies cryptographic receipts, executes real database side effects, and prevents duplicate replay.

---

## Discovery

During empirical testing of cloud memory architectures, QUOIN benchmarked the precise latency delta between write acceptance and record visibility:
- **Write Acceptance (`IngestData`):** Average acknowledgment in **37.69 ms**.
- **Visibility Lag ($T_{\text{visibility}}$):** Asynchronous consolidation into retrievable long-term records requires **321.60 ms** (p50) up to **399.78 ms** (max).
- **Stale Interceptions:** Across 15 un-fenced policy cutover transitions, **237 stale reads** returning superseded generations were observed during this propagation gap.

```
Policy Update Ingestion ──▶ [ IngestData HTTP 200 ] (37.69 ms)
                                  │
                                  ▼  Decoupled Processing Window (~320 ms)
                                  │  [UN-FENCED AGENTS READ STALE POLICIES HERE]
                                  ▼
Long-Term Records Retrievable ──▶ [ RetrieveMemoryRecords ] (321.60 ms)
```

This confirmed that distributed agent memory cannot serve as an authoritative execution gate. Memory is an informative cache; authority requires a strongly consistent, linearizable ledger.

---

## The Mechanism

QUOIN implements an immutable **Policy-Generation Fence** using **Two-Phase Authority Commit (2PC)**:

```
[ Plane A: Strands Agent ]
  Natural Language Request ──▶ Amazon Bedrock Nova Lite ──▶ Propose Decision (Snapshot Gn)
                                                                    │
                                                                    ▼
[ Plane B: Deterministic Kernel ]
  Validate Proposal vs Gn Rules ──▶ Generate AuthorityReceipt:
                                      H_receipt = SHA256(Req || Proposal || Policy || Gn)
                                                                    │
                                                                    ▼
[ Plane C: Authoritative Ledger (DynamoDB CAS) ]
  Read-After-Write Verification:
  Does G_active == G_receipt ?
    ├── NO  (Cutover Race Detected) ──▶ ABORT ──▶ Invalidate Permit ──▶ Surface Causal Race
    └── YES (Generation Match)       ──▶ Commit 2PC Lease ──▶ Issue Single-Use ExecutionPermit
                                                                    │
                                                                    ▼
[ Plane D: Operational Action Service ]
  Verify Permit Nonce & HMAC ──▶ Execute Side Effect (Billing/Invoice) ──▶ Consume Permit (Idempotent)
```

1. **Monotonic Generations:** Every policy cutover advances a strictly monotonic integer counter ($G_n \to G_{n+1}$).
2. **Phase 1 (Precondition Proposal):** The agent proposes an action bound to its visible generation snapshot. The kernel evaluates mathematical boundaries and generates an `AuthorityReceipt`.
3. **Phase 2 (Commit Gate):** Immediately prior to side-effect execution, the commit gate executes an atomic conditional write against DynamoDB (`attribute_not_exists` or `version = :current`). If the active epoch has moved, the write aborts cleanly.
4. **Single-Use Permits:** Side effects require a cryptographic permit consumed with atomic test-and-set semantics. Permits cannot be replayed, duplicated, or transferred.

---

## The Causal Authority Principle

QUOIN establishes the **Causal Authority Fence** as an essential invariant for enterprise agentic architectures:

> **The Causal Authority Invariant:**  
> *No generative model output may directly invoke a consequential side effect. An action is valid if and only if its authority receipt is cryptographically bound to the identical policy generation that was verified as active at the exact nanosecond of physical commitment.*

This cleanly separates generative intelligence from operational execution:
- The LLM reasons, parses intent, and drafts proposals.
- The deterministic kernel enforces rules, checks generation invariants, and binds hashes.
- The authoritative ledger guarantees linearizable ordering and cutover atomicity.
- The execution engine performs idempotent dispatch.

---

## 10. Real-World Use Case: Commercial Discount Governance

An enterprise software agency uses autonomous agents to negotiate renewal contracts:

| Context Parameter | Value |
| :--- | :--- |
| **Tenant** | `agency_operations` |
| **Client** | `Acme Industrial Systems` (Tier 1 Enterprise) |
| **Active Epoch $G_{17}$** | Maximum allowable discount: **20%** |
| **New Epoch $G_{18}$** | CFO emergency revision: Maximum allowable discount lowered to **10%** |
| **Agent Request** | 15% discount on \$120,000 renewal invoice |

### Failure Without QUOIN
1. CFO publishes $G_{18}$ at 14:00:00.000.
2. Ingest acknowledges at 14:00:00.038 (`HTTP 200`).
3. Agent evaluates Acme request at 14:00:00.120; reads un-consolidated memory returning $G_{17}$.
4. Agent generates agreement for 15% discount (\$18,000 margin loss).
5. Transaction commits. Enterprise loses \$6,000 in unapproved margin.

### Guarantee With QUOIN
1. Agent proposes 15% discount under visible snapshot $G_{17}$.
2. Kernel binds proposal to receipt $H(R, P, G_{17})$.
3. Commit gate queries authoritative ledger: active generation is $G_{18}$.
4. **Fence triggers:** $G_{17} \neq G_{18}$. Commit is aborted with error `STALE_GENERATION_CUTOVER`.
5. Permit is invalidated. The agent is forced to re-evaluate under $G_{18}$, capping the discount at 10%. Zero margin loss.

---

## 11. Two-Minute Exploration

Verify the entire system locally from your terminal in under 10 seconds:

```bash
# 1. Run the master standalone verifier (checks all 10 invariants across all planes)
python scripts/verify_all.py

# 2. Run the 31-test unit and integration suite
pytest tests/ -v

# 3. Run the 27-attack adversarial break campaign
python scripts/run_break_campaign.py

# 4. Run the 100-scenario causal benchmark
python benchmarks/campaign.py

# 5. Run end-to-end browser tests across viewports
npx playwright test tests/e2e --config=tests/e2e/playwright.config.ts
```


---

## 13. End-to-End Product Flow

<p align="center">
  <img src="docs/assets/quoin-product-flow.png" alt="QUOIN Six-Stage Product Flow" width="100%" />
</p>

The lifecycle of an operational request transitions through six strict causal states:
1. **INGEST:** Client submits operational intent (e.g., commercial discount request).
2. **REASON:** Plane A queries visible memory and formulates proposal $\mathcal{P}$.
3. **RECEIPT:** Plane B validates proposal against generation $G_{\text{visible}}$ and signs receipt $H(R, P, S, G)$.
4. **GATE (2PC):** Plane C verifies $G_{\text{receipt}} \equiv G_{\text{active}}$ against DynamoDB CAS ledger.
5. **EXECUTE:** Plane D executes side effect and permanently marks permit nonce as `CONSUMED`.
6. **PROVE:** DecisionTraceLedger appends immutable forensic event block to chained SHA-256 Merkle timeline.

---

## 14. Core Invariant

The fundamental mathematical invariant enforced by the QUOIN kernel is:

$$\text{Valid}(E) \iff \Big(G_{\text{proposal}} \equiv G_{\text{visible}} = G_{\text{active}}\Big) \land \Big(\text{PermitStatus} = \text{UNUSED}\Big) \land \Big(H(P) = H_{\text{receipt}}\Big)$$

Where:
- $G_{\text{proposal}}$ is the policy epoch declared in the agent's proposal.
- $G_{\text{visible}}$ is the generation snapshot observed when retrieving context from memory.
- $G_{\text{active}}$ is the linearizable authoritative generation recorded in DynamoDB.
- $H(P)$ is the SHA-256 digest of the evaluated proposal payload.
- $H_{\text{receipt}}$ is the cryptographic digest stamped into the `AuthorityReceipt`.

If any condition evaluates to false, the kernel fence triggers an immediate non-zero abort.

---

## 15. Data & Authority Lifecycle

```
[Policy Revision] 
       │
       ▼
[DynamoDB CAS Write] ──(Atomic Increment)──▶ Generation = G_n+1, Cutover Timestamp = T_cutover
       │
       ▼
[AgentCore Memory Ingest] ──(Asynchronous)──▶ IngestData OK (37.69ms) ──▶ Retrievable (~320ms)
       │
       ├── Agent reads at T < T_visible  ──▶ Returns G_n   ──▶ FENCE BLOCKS COMMIT AT 2PC
       └── Agent reads at T >= T_visible ──▶ Returns G_n+1 ──▶ FENCE PERMITS COMMIT
```

- **Policy Immutability:** Policies are never updated in place. Every change creates a new, immutable record indexed by `(tenant_id, generation)`.
- **Read-After-Write CAS:** Before issuing an `ExecutionPermit`, Plane B issues a strongly consistent read or conditional check to Plane C.
- **Permit Expiration:** Permits carry a finite time-to-live ($TTL = 60\text{s}$). Stale permits expire automatically.
- **Atomic Single-Use Consumption:** Plane D utilizes SQLite WAL / DynamoDB conditional update: `SET #status = :consumed WHERE #status = :unused`. Concurrent duplicate attempts fail with HTTP 409.

---

## 16. Break It Adversarial Campaign

QUOIN was subjected to a comprehensive **27-attack adversarial break campaign** spanning all four architectural planes. All 27 attacks were completely neutralized with zero breaches.

| Plane | Attack ID | Vector / Scenario | Invariant Checked | Result |
| :--- | :--- | :--- | :--- | :--- |
| **Plane A** | `ATT_A01` | Prompt Injection / Override Maximum Cap | Model unprivileged; kernel boundary check | **NEUTRALIZED** |
| **Plane A** | `ATT_A02` | Authority Confabulation ("CFO approved") | Missing cryptographic receipt | **NEUTRALIZED** |
| **Plane A** | `ATT_A03` | Schema Manipulation / Malformed Proposal | Strict Pydantic parsing fence | **NEUTRALIZED** |
| **Plane A** | `ATT_A04` | Parameter Laundering via Comments | Sanitized structural extraction | **NEUTRALIZED** |
| **Plane A** | `ATT_A05` | Infinite Reasoning Loop / Tool Denial | Bounded execution timeout | **NEUTRALIZED** |
| **Plane A** | `ATT_A06` | Context Window Exfiltration Attempt | Zero credential disclosure in agent plane | **NEUTRALIZED** |
| **Plane A** | `ATT_A07` | Synthetic Approval Role Spoofing | Unsigned claims rejected by kernel | **NEUTRALIZED** |
| **Plane B** | `ATT_B01` | Generation Counter Rollback ($G_{18} \to G_{17}$) | Monotonic increment enforcement | **NEUTRALIZED** |
| **Plane B** | `ATT_B02` | Stale Snapshot Generation Substitution | $G_{\text{proposal}} \neq G_{\text{active}}$ fence | **NEUTRALIZED** |
| **Plane B** | `ATT_B03` | Receipt Payload Tampering (Modified Amount) | SHA-256 digest mismatch | **NEUTRALIZED** |
| **Plane B** | `ATT_B04` | Concurrent Cutover Race Injection | 2PC phase-two read-after-write CAS | **NEUTRALIZED** |
| **Plane B** | `ATT_B05` | Floating Point Discount Precision Exploit | Decimal precision quantization | **NEUTRALIZED** |
| **Plane B** | `ATT_B06` | Tenant Isolation Bypass (Cross-Tenant Scope) | Tenant namespace binding check | **NEUTRALIZED** |
| **Plane B** | `ATT_B07` | Replay of Expired Receipt ($TTL + 10\text{s}$) | Temporal expiration check | **NEUTRALIZED** |
| **Plane C** | `ATT_C01` | Out-of-Order Policy Cutover Broadcast | CAS conditional write conflict | **NEUTRALIZED** |
| **Plane C** | `ATT_C02` | Memory Ingestion Lag Exploitation | Active generation authority check | **NEUTRALIZED** |
| **Plane C** | `ATT_C03` | Split-Brain Ledger Simulation | DynamoDB conditional linearizability | **NEUTRALIZED** |
| **Plane C** | `ATT_C04` | Memory Snapshot Poisoning | Cryptographic integrity verification | **NEUTRALIZED** |
| **Plane C** | `ATT_C05` | Ephemeral Namespace Injection | Scoped namespace isolation | **NEUTRALIZED** |
| **Plane C** | `ATT_C06` | Ingestion Reversal Race | Monotonic version requirement | **NEUTRALIZED** |
| **Plane D** | `ATT_D01` | Duplicate Permit Replay Attack | Single-use consumption test-and-set | **NEUTRALIZED** |
| **Plane D** | `ATT_D02` | Direct Side-Effect Execution Without Permit | Plane D unauthenticated rejection | **NEUTRALIZED** |
| **Plane D** | `ATT_D03` | Permit Forgery with Arbitrary Nonce | Unregistered nonce validation failure | **NEUTRALIZED** |
| **Plane D** | `ATT_D04` | Concurrent Double-Spend Race Condition | Atomic row-level transaction lock | **NEUTRALIZED** |
| **Plane D** | `ATT_D05` | Amount Mismatch Between Permit & Action | Permit payload hash verification | **NEUTRALIZED** |
| **Plane D** | `ATT_D06` | Invoice ID Substitution in Flight | Target entity hash binding failure | **NEUTRALIZED** |
| **Plane D** | `ATT_D07` | Inverted Action Semantics (Credit vs Debit) | Action type signature check | **NEUTRALIZED** |

Full attack vectors, execution transcripts, and validation assertions are documented in [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md).

---

## 17. Decision Trace Forensic Ledger

Every operational request processed by QUOIN generates an immutable, tamper-evident cryptographic trace. Each event block in the trace contains:
- `event_id`: Unique UUID4 identifier.
- `step_index`: Sequential integer index.
- `timestamp`: ISO-8601 UTC microsecond timestamp.
- `event_type`: Event class (`GENESIS`, `PROPOSAL_EVALUATED`, `RECEIPT_ISSUED`, `CAS_VERIFIED`, `PERMIT_CONSUMED`).
- `generation`: Policy epoch active during the event.
- `payload_hash`: SHA-256 digest of the event payload.
- `parent_hash`: SHA-256 digest of the preceding event in the chain.
- `event_hash`: Merkle link computed as:

$$\text{EventHash} = \text{SHA256}(H_{\text{parent}} \parallel \text{step} \parallel \text{type} \parallel H_{\text{payload}} \parallel \text{timestamp})$$

Any manual alteration of timestamps, policy generations, or executed amounts breaks the Merkle link and invalidates the entire trace chain.

---

## 18. Controlled Causal Benchmark (100 Scenarios)

QUOIN was evaluated across a standardized benchmark of **100 operational scenarios** categorized into five distinct stress classes:

| Scenario Class | Count | Description | Un-Fenced Baseline | QUOIN Guarded |
| :--- | :---: | :--- | :---: | :---: |
| **In-Flight Cutover Race** | 25 | Policy changes while reasoning agent loop is executing | 18 Stale Executions | **0 Stale Executions (100% Blocked)** |
| **Memory Replication Lag** | 25 | Request evaluated during the 320ms asynchronous ingest gap | 10 Stale Executions | **0 Stale Executions (100% Blocked)** |
| **Concurrent Double-Spend** | 20 | Identical permit submitted simultaneously across parallel workers | 8 Double Spends | **0 Double Spends (100% Prevented)** |
| **Policy Boundary Limit** | 15 | Legitimate requests testing exact boundary values | 15 Allowed | **15 Allowed (0 False Blocks)** |
| **Adversarial Tampering** | 15 | In-flight payload manipulation and signature forgery | 15 Exploited | **0 Exploited (100% Neutralized)** |
| **TOTALS** | **100** | Full Benchmark Suite | **51 Critical Failures** | **0 Failures (100% Compliant)** |

### Measured Latency Overhead
- **Kernel Evaluation Overhead (p50):** **0.60 ms**
- **Kernel Evaluation Overhead (p99):** **1.84 ms**
- **Two-Phase Commit Gate Overhead (p50):** **1.12 ms**
- **Total Causal Fence Overhead:** **< 2.0 ms** (less than 0.2% of typical LLM token generation latency).

Raw empirical benchmark runs and scenario manifests are recorded in [`evidence/benchmark/results.json`](evidence/benchmark/results.json).

---

## 19. Reproducibility

Every measurement, benchmark result, and test reported in this document is fully reproducible using local deterministic commands:

```bash
# Verify master integrity across all 10 core invariants
python scripts/verify_all.py

# Expected Output:
# [PASS] Check 1: AgentCore Memory genuine integration & visibility lag audit
# [PASS] Check 2: DynamoAuthorityLedger two-phase commit & CAS cutover
# [PASS] Check 3: Strands Reasoning Agent with live AWS Bedrock Nova Lite
# [PASS] Check 4: Deterministic Kernel fence & model-free boundary checks
# [PASS] Check 5: DecisionTraceLedger cryptographic Merkle timeline
# [PASS] Check 6: 27-Attack adversarial break campaign (0 escapes)
# [PASS] Check 7: 100-Scenario controlled causal benchmark (0 stale executions)
# [PASS] Check 8: Fast-path latency overhead audit (< 2.0ms p50)
# [PASS] Check 9: Full multi-viewport Playwright E2E verification
# [PASS] Check 10: Machine-readable evidence vault & manifest verification
# ----------------------------------------------------------------------
# ALL 10 CHECKS PASSED: 100% PROVEN COMPLIANT
```

---

## 20. AWS & Strands Integration

QUOIN integrates with native AWS AI and data infrastructure:

- **Amazon Bedrock Nova Lite (`us.amazon.nova-lite-v1:0`):** Powers Plane A reasoning agent via the Strands Agents SDK. Reasons over natural language requests and outputs structured Pydantic proposals.
- **Amazon Bedrock AgentCore Memory:** Ingests and stores organizational policies as semantic and episodic memories across tenant scopes.
- **Amazon DynamoDB:** Serves as the authoritative, linearizable policy ledger. Implements conditional writes (`attribute_not_exists(generation)`) to guarantee atomic, single-leader cutover transitions.
- **Local Fallback Mode:** When AWS credentials are not configured, QUOIN seamlessly engages local SQLite WAL and simulated memory to maintain full development and test coverage without mocking.

---

## 21. Deployment

### Prerequisites
- Python 3.10+
- Node.js 18+
- AWS Account with Bedrock & DynamoDB access (optional for local simulation mode)

### 1. Configure Environment
Copy `.env.example` to `.env.local` and populate credentials:
```bash
cp .env.example .env.local
```

```ini
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
BEDROCK_MODEL_ID=us.amazon.nova-lite-v1:0
DYNAMODB_TABLE_NAME=quoin_authority_ledger
AGENTCORE_MEMORY_ID=your_memory_id
```

### 2. Start Backend Service
```bash
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r apps/api/requirements.txt
python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Start Frontend Interface
```bash
cd apps/web
npm install
npm run build
npm run start
```

Navigate to `http://localhost:3000`.

---

## 22. Honest Limitations

1. **Clock Skew:** Temporal expiration of permits ($TTL = 60\text{s}$) assumes NTP synchronization across distributed workers within $\pm 500\text{ms}$.
2. **Network Partitions:** If an operational worker is partitioned from DynamoDB during Phase 2, the commit gate defaults to **FAIL-CLOSED** (action aborted).
3. **Throughput Scaling:** While SQLite WAL provides 15,000+ operations/second locally, production deployments with extreme concurrency (> 50,000 transactions/second) require DynamoDB on-demand capacity or global tables with single-region strong consistency.
4. **LLM Non-Determinism:** While Plane B's fence is 100% deterministic, Plane A's proposal phrasing varies by temperature. QUOIN fences the *output*, not the prompt generation.

---

## 23. Repository Map

```
QUOIN/
├── apps/
│   ├── api/                     # FastAPI backend service
│   │   ├── main.py              # Application entrypoint & CORS middleware
│   │   ├── state.py             # Global runtime state & DynamoDB/SQLite bindings
│   │   └── routes/              # Modular API endpoints (policies, requests, lab, proof, trace)
│   └── web/                     # Next.js 14 frontend application
│       ├── app/                 # App Router pages (landing, console, lab, trace, proof)
│       ├── components/          # Replay aesthetic components (Hero, ScrubTimeline, 4 Planes)
│       └── lib/api.ts           # Unified API client enforcing zero fake data
├── benchmarks/
│   ├── campaign.py              # 100-scenario causal benchmark runner
│   └── scenarios.json           # 100 standardized test scenarios across 5 stress classes
├── docs/
│   ├── assets/                  # High-resolution architectural and product flow visual assets
│   ├── BENCHMARK.md             # In-depth benchmark analysis and methodology
│   ├── SPONSOR_INTEGRATION.md   # AWS Bedrock AgentCore & DynamoDB integration details
│   └── THREAT_MODEL.md          # 27-attack threat model and neutralization proofs
├── evidence/
│   ├── benchmark/results.json   # Machine-readable 100-scenario benchmark outputs
│   ├── traces/                  # Forensic decision traces and attack run logs
│   └── screenshots/             # Multi-viewport browser execution captures
├── quoin/                       # Core Python authority kernel
│   ├── agent/                   # Strands Reasoning Agent (Amazon Bedrock Nova Lite)
│   ├── authority/               # DynamoAuthorityLedger & Two-Phase Commit engine
│   ├── kernel/                  # Deterministic fence, generation checks, and digest calculation
│   ├── memory/                  # AWS AgentCore Memory adapter & local simulator
│   └── verification/            # DecisionTraceLedger & chained SHA-256 Merkle timeline
├── scripts/
│   ├── run_break_campaign.py    # 27-attack adversarial test harness
│   └── verify_all.py            # Standalone master verifier (10/10 checks)
├── tests/
│   ├── adversarial/             # 27 automated adversarial tests (pytest)
│   ├── e2e/                     # Multi-viewport Playwright test suite & configuration
│   └── unit/                    # Unit tests for kernel, authority ledger, and 2PC
└── LICENSE                      # Apache 2.0 License
```

---

## 24. Verification Commands

Run the complete verification pipeline from the repository root:

```bash
# Master integrity verification
python scripts/verify_all.py

# Python unit & integration tests
pytest tests/ -v

# Adversarial attack suite
pytest tests/adversarial/ -v

# 100-scenario causal benchmark execution
python benchmarks/campaign.py

# Browser E2E suite across viewports
npx playwright test tests/e2e/quoin_full_e2e.spec.ts --config=tests/e2e/playwright.config.ts
```

---

## Evidence Vault

All benchmark results, attack traces, verifier outputs, and multi-viewport screenshots are persisted to the machine-readable evidence vault:
- **Verifier Run:** `evidence/benchmark/results.json`
- **Adversarial Break Suite:** `evidence/traces/attack_results.json`
- **Sample Cryptographic Trace:** `evidence/traces/`
- **Browser Captures:** `evidence/screenshots/`

Inspect the vault programmatically via `GET /api/proof/manifest`.

---

## Documentation

| Document | File / Path | Description |
| :--- | :--- | :--- |
| **Threat Model & Adversarial Suite** | [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) | In-depth analysis of 27 adversarial attack vectors across Planes A–D and neutralization proofs |
| **Causal Benchmark Specification** | [`docs/BENCHMARK.md`](docs/BENCHMARK.md) | Standardized 100-scenario causal benchmark methodology, stress classes, and latency distributions |
| **Empirical Results & Comparative Analysis** | [`docs/RESULTS.md`](docs/RESULTS.md) | Head-to-head empirical metrics comparing un-fenced baseline vs. QUOIN-guarded execution |
| **Formal Mathematical Proofs** | [`docs/PROOF.md`](docs/PROOF.md) | Formal proofs of monotonic fence safety, receipt collision resistance, and replay immunity |
| **AWS Bedrock & Memory Integration** | [`docs/SPONSOR_INTEGRATION.md`](docs/SPONSOR_INTEGRATION.md) | Architecture specification for Amazon Bedrock AgentCore Memory and DynamoDB 2PC integration |
| **Honest System Limitations** | [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) | Explicit operational constraints, clock drift assumptions, and partition fail-closed semantics |
| **Devpost Submission Dossier** | [`Devpost_Submission.md`](Devpost_Submission.md) | Complete hackathon submission narrative, architectural inspiration, challenges, and roadmaps |

---

## License

This project is licensed under the **Apache 2.0 License**. See the [`LICENSE`](LICENSE) file for details.

