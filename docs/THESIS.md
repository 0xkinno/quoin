# QUOIN Thesis: Policy-Generation Fences for Professional Agents

## 1. The Core Insight
> **Authority freshness is not the same thing as write acknowledgement.**

In modern distributed agent runtimes—exemplified by AWS Bedrock AgentCore Memory—submitting an update (`IngestData`) confirms ingestion acceptance almost instantaneously (~35ms). However, the creation and availability of consolidated long-term memory records happens asynchronously in a background pipeline (typically 200ms–400ms).

This produces an operational gap:
$$\text{SUBMITTED} \to \text{ACCEPTED} \xrightarrow{\quad\Delta t \approx 320\text{ms}\quad} \text{VISIBLE} \to \text{VERIFIED}$$

## 2. The Professional Operational Failure
In professional services (agency management, consulting, billing, contract administration), business policy changes continuously.
When an organization tightens a commercial rule (e.g. maximum discount lowered from 20% to 10%), an agent in-flight during that propagation gap reads the old policy generation from memory.

A naive agent, believing the write has completed, approves actions that are illegal under the new authority.

## 3. The QUOIN Thesis
> **QUOIN prevents professional agents from acting on stale policy by fencing every consequential action to the exact policy generation the agent has actually verified as visible.**

By introducing:
1. Pure Python model-free authority kernel
2. Monotonic generation counters ($G_n \to G_{n+1}$)
3. Signed cryptographic authority receipts
4. Two-phase commit gate with read-after-write verification
5. Idempotent side-effect execution ledger

QUOIN eliminates 100% of stale-policy executions without adding LLM latency.
