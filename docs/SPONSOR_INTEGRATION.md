# Sponsor Integration: AWS Bedrock AgentCore & Strands

QUOIN integrates AWS AgentCore and Strands as **load-bearing architectural primitives**:

## 1. Amazon Bedrock AgentCore Memory
- **Decoupled Lifecycle Utilization:** Rather than ignoring the asynchronous consolidation delay between `IngestData` and `RetrieveMemoryRecords`, QUOIN treats this physical boundary as an explicit authority state transition.
- **Namespaces:** Multi-tenant isolation using `/quoin/{tenant_id}/policy`, `/quoin/{tenant_id}/policy_history`, and `/quoin/{tenant_id}/decisions`.
- **Structured Metadata:** Attaches deterministic metadata (`generation`, `version_hash`, `effective_at`) to every ingested policy record to enable cryptographic validation.

## 2. Amazon Bedrock
- Foundational model runtime powering the Strands decision plane for operational request analysis and proposal synthesis.

## 3. Strands Agents SDK
- **Reasoning Architecture:** Uses official `strands-agents` SDK (`Agent`, `tool`) to intake client requests and propose actions.
- **Architectural Boundary:** The Strands agent proposes actions through the `ProposalAdapter` without having direct execution authority or access to the kernel commit gate.
