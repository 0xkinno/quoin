# Sponsor Discovery: Accepted is Not Visible

## Executive Summary
In distributed agent architectures utilizing **AWS Bedrock AgentCore Memory**, data ingestion and semantic record retrievability operate on decoupled asynchronous lifecycles.

Empirical measurement confirms:
- **Write Acknowledgment (`IngestData`):** Acknowledged synchronously in an average of **37.69 ms**.
- **Visibility Lag Interval ($T_{\text{visibility}}$):** Long-term memory records become observable in the decision loop only after an asynchronous consolidation window:
  - **Min:** 210.06 ms
  - **p50 (Median):** 321.60 ms
  - **p90:** 378.04 ms
  - **p95:** 392.96 ms
  - **Max:** 399.78 ms

During this critical window, immediate reads against the memory store return the **prior, stale generation** or empty states. In our controlled trials across 15 policy cutover events, a total of **237 stale reads** were observed.

## The Operational Failure in Professional Agents
When professional operational policies change (e.g., maximum allowable discount reduced from 20% to 10%), an agent in-flight will query AgentCore Memory during the visibility window. Because the write has succeeded, the organization assumes the new policy is live. However, because the memory records are still processing, the agent reads the superseded generation and authorizes an invalid, out-of-policy transaction.

## The QUOIN Solution
QUOIN formalizes this infrastructure boundary as an explicit authority state machine:
$$\text{SUBMITTED} \to \text{ACCEPTED} \to \text{PROCESSING} \to \text{VISIBLE} \to \text{VERIFIED}$$

No consequential action may cross the **policy-generation fence** until the authority receipt matches the exact policy generation confirmed visible at the final execution gate.
