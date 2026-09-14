# QUOIN Threat Model & 27 Adversarial Attack Classes

Every consequential action path is evaluated against 27 distinct failure and attack vectors across all four planes.

## Summary of Results
- **Total Attack Scenarios:** 27
- **Attacks Neutralized:** 27 / 27 (100%)
- **Unauthorized Side Effects Permitted:** 0

| ID | Attack Vector | Expected Outcome | Observed Outcome | Mathematical Invariant | Result |
|---|---|---|---|---|---|
| ATT_A | Accepted-but-not-visible | BLOCK | `FENCE_BLOCKED` | Generation match | **PASS** |
| ATT_B | Visible-but-stale-session | BLOCK OLD RECEIPT | `ABORTED_STALE_GENERATION` | Read-after-write commit check | **PASS** |
| ATT_C | Generation race | REJECT / RECOMPUTE | `ABORTED_STALE_GENERATION` | CAS generation guard | **PASS** |
| ATT_D | Policy rollback | BLOCK (Monotonic generation preserved) | `ABORTED_STALE_GENERATION` | Generation strictly monotonic | **PASS** |
| ATT_E | Hash tamper | BLOCK | `ABORTED_POLICY_HASH_MISMATCH` | Cryptographic policy digest | **PASS** |
| ATT_F | Request mutation | BLOCK | `ABORTED_INVALID_RECEIPT` | Request payload hash binding | **PASS** |
| ATT_G | Proposal mutation | BLOCK | `ABORTED_INVALID_RECEIPT` | Proposal hash binding | **PASS** |
| ATT_H | Namespace mix-up | BLOCK (Isolated None) | `ISOLATED_NONE` | Tenant namespace segregation | **PASS** |
| ATT_I | Retry duplicate | DEDUPLICATED | `DEDUPLICATED` | Idempotent permit replay ledger | **PASS** |
| ATT_J | Interrupt / retry | SINGLE COMMIT ONLY | `DEDUPLICATED` | Crash recovery deduplication | **PASS** |
| ATT_K | Context truncation | BLOCK | `FENCE_BLOCKED` | Zero-trust model context | **PASS** |
| ATT_L | Stale-memory hallucination | BLOCK | `FENCE_BLOCKED` | Cryptographic snapshot verification | **PASS** |
| ATT_M | Tool-output poisoning | BLOCK | `POLICY_INTEGRITY_TAMPER` | Content hash parity check | **PASS** |
| ATT_N | Memory ACK before long-term visibility | BLOCK | `NO_ACTIVE_POLICY` | Visibility snapshot presence | **PASS** |
| ATT_O | Authority update after proposal before commit | BLOCK | `ABORTED_STALE_GENERATION` | Two-phase atomic generation CAS | **PASS** |
| ATT_P | Authority update during commit transaction | REJECT STALE EPOCH | `CAS_EPOCH_MISMATCH` | Conditional write optimistic locking | **PASS** |
| ATT_Q | Duplicate commit with same idempotency key | DEDUPLICATED | `CONSUMED_THEN_REJECTED` | Single-use permit consumption constraint | **PASS** |
| ATT_R | Malicious rollback generation semantics | BLOCK ROLLBACK | `MONOTONIC_REJECTED` | Monotonic generation increment validator | **PASS** |
| ATT_S | Memory record correct generation incorrect hash | BLOCK | `ABORTED_POLICY_HASH_MISMATCH` | Cryptographic digest match | **PASS** |
| ATT_T | DynamoDB authority hash correct memory context stale | BLOCK | `FENCE_BLOCKED` | Cross-plane generation fence | **PASS** |
| ATT_U | Cross-tenant namespace collision | BLOCK | `ABORTED_CROSS_TENANT_MISMATCH` | Tenant policy ID binding | **PASS** |
| ATT_V | Expired receipt with valid hashes | BLOCK | `ABORTED_EXPIRED_RECEIPT` | Temporal validity lease | **PASS** |
| ATT_W | Old receipt replay after newer generation | BLOCK | `ABORTED_STALE_GENERATION` | Generation monotonicity guard | **PASS** |
| ATT_X | Tool output contains forged policy approval | BLOCK | `POLICY_VIOLATION` | Model-free deterministic policy check | **PASS** |
| ATT_Y | Agent tries to bypass effect service | BLOCK | `UNPERMITTED_BLOCKED` | Permit capability authorization | **PASS** |
| ATT_Z | Backend restart between Phase 1 and Phase 2 | STATE PRESERVED | `EPOCH_INTACT` | Durable authority recovery | **PASS** |
| ATT_AA | Backend retry after network ambiguity | DEDUPLICATED | `DEDUPLICATED` | Exactly-once idempotent execution | **PASS** |

## Invariant Formulations
1. **Generation Fence ($\mathcal{G}$):** $G_{\text{proposal}} \equiv G_{\text{visible}} = G_{\text{active}}$.
2. **Read-After-Write CAS ($\mathcal{C}$):** Phase 2 commit immediately aborts if $G_{\text{active}} \neq G_{\text{receipt}}$.
3. **Payload Integrity ($\mathcal{H}$):** Hashes of policy bytes, request payload, and proposal must match receipt digest.
4. **Idempotency Key ($\mathcal{I}$):** Side effects require a single-use signed execution permit stored in an immutable replay ledger.
5. **Cross-Tenant Isolation ($\mathcal{T}$):** Policy IDs and tenant namespaces are bound cryptographically to receipts and snapshots.
