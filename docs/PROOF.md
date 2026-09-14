# Mathematical & Cryptographic Proof of QUOIN Fences

## Theorem 1: Stale Action Non-Execution (Safety Invariant)
**Statement:** An action evaluated under policy generation $G_a$ cannot execute under policy generation $G_b$ when $G_b > G_a$.

**Proof by Contradiction:**
1. Assume an action evaluated under $G_a$ executes while active authority is $G_b$ ($G_b > G_a$).
2. By the Two-Phase Commit Gate specification, an action commits only if an `ExecutionPermit` is issued by the kernel.
3. The kernel issues an `ExecutionPermit` if and only if $\mathcal{R}.\text{policy\_generation} = G_{\text{readback}}$.
4. In Phase 2, $G_{\text{readback}}$ is retrieved directly from the memory reader immediately before commit.
5. Since active authority is $G_b$, $G_{\text{readback}} = G_b$.
6. The receipt was generated under $G_a$, therefore $\mathcal{R}.\text{policy\_generation} = G_a$.
7. Since $G_b > G_a$, $\mathcal{R}.\text{policy\_generation} \neq G_{\text{readback}}$.
8. Therefore, the equality predicate fails, the receipt is permanently invalidated, and `CommitResult.committed` evaluates to `false`.
9. This contradicts step 1. Thus, no action evaluated under $G_a$ can execute under $G_b$. $\blacksquare$

## Theorem 2: Tamper Resistance via Cryptographic Digest Binding
**Statement:** Any modification to the request payload $R \to R'$ after receipt issuance is detected and blocked with probability $1 - 2^{-256}$.

**Proof:**
1. The authority receipt $\mathcal{R}$ binds $H_R = \mathcal{H}(R) = \text{SHA256}(\text{Canonical}(R))$.
2. In Phase 2, the commit gate receives $R'$ and computes $H_{R'} = \text{SHA256}(\text{Canonical}(R'))$.
3. If $R \neq R'$, then $H_R = H_{R'}$ would require finding a second pre-image or collision in SHA-256.
4. Under the standard cryptographic assumption that SHA-256 is collision-resistant, $H_R \neq H_{R'}$.
5. The commit gate enforces $H_R == H_{R'}$; upon failure, status evaluates to `ABORTED_TAMPER_REQUEST`. $\blacksquare$

## Theorem 3: Idempotency & Replay Immunity
**Statement:** Submitting the same execution permit $k$ times ($k \ge 2$) produces at most 1 state mutation in the effect plane.

**Proof:**
1. Plane D actions require passing a signed `ExecutionPermit` with unique `permit_id`.
2. Upon first execution ($k = 1$), `IdempotencyLedger.record_execution` atomically registers `permit_id` in an immutable map before returning the result.
3. For all subsequent calls ($k \ge 2$), `IdempotencyLedger.get_existing(permit_id)` matches the recorded key and returns status `DEDUPLICATED` without executing the side-effect handler.
4. Total executed mutations $M = 1$. $\blacksquare$
