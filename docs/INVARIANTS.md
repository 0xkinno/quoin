# QUOIN Constitutional Invariants

QUOIN enforces an unambiguous mathematical predicate governing all consequential side effects.

## The Primary Invariant
> **No consequential action may execute unless its authority receipt is bound to the same verified policy generation that is currently visible to the agent’s decision loop and still valid at the final execution gate.**

## Formal Specification

Let:
- $R$ be an incoming operational request.
- $P_{\text{active}}$ be the policy record verified as currently visible in memory.
- $G_{\text{active}} \in \mathbb{N}$ be the generation number of $P_{\text{active}}$.
- $\mathcal{H}(x)$ be the deterministic canonical SHA-256 digest of $x$.
- $\text{Prop}$ be the candidate decision proposal.
- $\mathcal{R}$ be the issued authority receipt.
- $E$ be the intended operational side effect.
- $t_{\text{now}}$ be the system UTC timestamp at Phase 2 commit.

Execution is permitted if and only if all eight conditions hold:

$$\text{EXECUTE}(E) \iff \begin{cases}
1. & \mathcal{R}.\text{valid} = \text{true} \\
2. & \mathcal{R}.\text{policy\_generation} = G_{\text{active}} \\
3. & \mathcal{R}.\text{policy\_hash} = \mathcal{H}(P_{\text{active}}) \\
4. & \mathcal{R}.\text{request\_hash} = \mathcal{H}(R) \\
5. & \mathcal{R}.\text{proposal\_hash} = \mathcal{H}(\text{Prop}) \\
6. & \mathcal{R}.\text{effect\_hash} = \mathcal{H}(E) \\
7. & t_{\text{now}} < \mathcal{R}.\text{expires\_at} \\
8. & \text{Readback}(P_{\text{active}}) \equiv P_{\text{active}}
\end{cases}$$

## Fallback Semantics
If any predicate evaluates to $\text{false}$:
$$\text{ABORT} \implies \text{Invalidate}(\mathcal{R}) \to \text{Re-evaluate under } G_{\text{active}} \lor \text{Escalate to Human}$$

Zero side effects are dispatched under failed predicates.
