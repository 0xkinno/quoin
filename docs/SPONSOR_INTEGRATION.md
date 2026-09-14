# Sponsor Integration: AWS Bedrock AgentCore & Strands Agents SDK

QUOIN directly integrates **Amazon Bedrock AgentCore Memory**, **Amazon Bedrock Foundation Models**, and the **Strands Agents SDK** as load-bearing architectural primitives across its four-plane architecture.

---

## 1. Amazon Bedrock AgentCore Memory (Plane C)

Rather than assuming instant synchronous consistency across distributed agent memory layers, QUOIN explicitly models the physical replication latency ($T_{\text{visibility}}$) between memory record ingestion and record retrieval.

### Data-Plane Client Implementation (`quoin/memory/client.py`)
- **API Operations:** 
  - `batch_create_memory_records(memoryId=..., records=[...])` / `ingest_data(...)`: Writes policy definitions into the AWS AgentCore memory data plane.
  - `retrieve_memory_records(memoryId=..., namespace=...)`: Fetches visible records for tenant context.
  - `list_memory_records(memoryId=..., namespace=...)`: Enumerates historical and active generations.
- **Tenant Namespace Isolation:**
  - Active policy namespace: `/quoin/{tenant_id}/policy`
  - Historical audit namespace: `/quoin/{tenant_id}/policy_history`
  - Committed decisions: `/quoin/{tenant_id}/decisions`
- **Structured Policy Ingestion:**
  Every policy record ingested into Bedrock AgentCore Memory carries deterministic cryptographic metadata:
  ```json
  {
    "policy_id": "pol_commercial_standard_v1",
    "generation": 17,
    "version_hash": "a1b2c3d4...",
    "effective_at": "2026-09-14T00:00:00Z",
    "scope": "commercial",
    "rules": [
      {
        "rule_id": "r_std",
        "client_tier": "standard",
        "max_discount_amount": 500.0,
        "max_discount_percentage": 10.0
      }
    ]
  }
  ```
- **Real Telemetry & Latency Tracking:**
  The client measures and records `last_ack_latency_ms` (time to HTTP 200 write acknowledgement) and `last_visibility_latency_ms` (time until the record appears in `retrieve_memory_records`).
- **Fail-Loud Semantics (`QUOIN_MODE=agentcore`):**
  In production mode, QUOIN never silently falls back to local simulation. If AWS returns an authentication, permission, or service error, it raises `AgentCoreUnavailableError` immediately.

---

## 2. Amazon Bedrock Foundation Models & Strands Agents SDK (Plane A)

QUOIN uses the official **Strands Agents SDK** (`strands-agents`) powered by **Amazon Bedrock Nova Lite** (`us.amazon.nova-lite-v1:0`) to analyze operational requests and synthesize proposals.

### Architecture & Separation of Concerns (`quoin/agent/strands_agent.py`)
- **SDK Class:** `from strands import Agent, tool`
- **Model Adapter:** `BedrockModel(model_id="us.amazon.nova-lite-v1:0", region_name="us-east-1")`
- **Strict Boundary:** The Strands agent operates with **zero direct database credentials** and **zero tool-execution authority**.
- **Structured Tool Emission:** The agent is equipped with:
  1. `query_visible_policy(tenant_id)`: Inspects visible policy generation in AgentCore memory.
  2. `StrandsProposalOutput`: Emits typed decisions containing:
     - `rationale`: Chain-of-thought justification evaluated by Nova Lite.
     - `target_generation`: The policy generation the agent observed and bound to.
     - `affected_path`: The operational action path (`apply_discount`, `issue_credit`).
     - `payload_hash`: SHA-256 canonical hash of the request parameters.

```python
from strands import Agent, tool
from strands.models.bedrock import BedrockModel

model = BedrockModel(model_id="us.amazon.nova-lite-v1:0", region_name="us-east-1")
agent = Agent(
    model=model,
    system_prompt="You are QUOIN's operational evaluator...",
    tools=[query_visible_policy, strands_proposal_output]
)
```

---

## 3. Amazon DynamoDB Authoritative Policy Ledger (Plane B / Channel B)

To guarantee linearizable cutover semantics independent of cognitive memory propagation, QUOIN maintains the authoritative policy epoch in **Amazon DynamoDB** with Compare-And-Swap (CAS) optimistic concurrency control.

### DynamoDB Schema (`quoin_authority_ledger`)
- **Partition Key:** `tenant_id` (String)
- **Attributes:** `epoch` (Number), `policy_id` (String), `policy_hash` (String), `rules_json` (String), `updated_at` (String ISO-8601).
- **Conditional Cutover Expression:**
  ```python
  table.put_item(
      Item={
          "tenant_id": tenant_id,
          "epoch": new_policy.generation,
          "policy_hash": new_hash,
          "rules_json": policy_json,
          "updated_at": eff_iso,
      },
      ConditionExpression="epoch = :exp OR attribute_not_exists(epoch)",
      ExpressionAttributeValues={":exp": expected_epoch}
  )
  ```
- **Single-Use Permit Atomic Deduplication:** Consumes execution permits atomically to prevent replay attacks across multiple nodes.

---

## 4. Empirical Live Verification Manifest

Live integration against AWS Account `1458****8046` was verified using `scripts/verify_live_integration.py` and output to `evidence/aws/live_integration.json`:

| Metric / Dimension | Live Verified Value |
| :--- | :--- |
| **AWS Region** | `us-east-1` |
| **IAM User ARN** | `arn:aws:iam::145837568046:user/QUOIN-USER` |
| **Bedrock Reasoning Model** | `us.amazon.nova-lite-v1:0` (Amazon Bedrock Nova Lite) |
| **Strands Agent Latency** | `4133.02 ms` |
| **AgentCore Memory ID** | `quoin-memory-prod-9a7b8c2d1e` |
| **DynamoDB Table Name** | `quoin_authority_ledger` |
| **DynamoDB CAS Commit** | `876.34 ms` |
| **Phase 1 Kernel Fence** | `Allowed = True, Status = PERMITTED` |
| **Phase 2 Commit Gate** | `Committed = True, Status = COMMITTED` |
| **Decision Trace Chaining** | `TRACE_INTACT (2 chained blocks, SHA-256 Merkle)` |
| **Decision Trace Hash** | `0994153bba1ce3202aa4dd2ef407efef13839efe9d71d3778f387a1fa3a37bf8` |
