"""Core data models for QUOIN deterministic authority plane."""

from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional, Dict
from pydantic import BaseModel, Field

class PolicyRule(BaseModel):
    """Specific operational rule within an authority policy."""
    rule_id: str
    scope: str = "general"
    client_tier: Optional[str] = None
    max_discount_percentage: float = 0.0
    max_discount_amount: float = 0.0
    max_credit_amount: float = 0.0
    max_acceleration_days: int = 0
    max_scope_hours: int = 0
    requires_escalation: bool = False
    margin_floor_percentage: float = 0.0
    note: Optional[str] = None

class PolicyRecord(BaseModel):
    """Canonical policy document state at a specific generation."""
    policy_id: str
    generation: int
    version_hash: str
    effective_at: datetime
    scope: str
    rules: List[PolicyRule] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PolicyUpdate(BaseModel):
    """Monotonic mutation record advancing policy generation."""
    policy_id: str
    previous_generation: int
    next_generation: int
    version_hash: str
    submitted_at: datetime
    memory_write_token: Optional[str] = None

class AuthoritySnapshot(BaseModel):
    """Read snapshot of active authority verified by the memory plane."""
    policy_id: str
    generation: int
    visible_at: datetime
    source: str
    retrieved_record_hash: str
    namespace: str
    policy_record: Optional[PolicyRecord] = None

class DecisionProposal(BaseModel):
    """Reasoning plane proposal for a consequential operational action."""
    request_id: str
    requested_action: str
    requested_value: Optional[float] = None
    rationale: str = ""
    candidate_policy_generation: int
    parameters: Dict[str, Any] = Field(default_factory=dict)

class AuthorityReceipt(BaseModel):
    """Cryptographically bound receipt certifying compliance with a verified policy generation."""
    receipt_id: str
    request_id: str
    policy_id: str
    policy_generation: int
    policy_hash: str
    request_hash: str
    proposal_hash: str
    authority_snapshot_hash: str = ""
    effect_hash: str = ""
    issued_at: datetime
    expires_at: datetime
    kernel_version: str = "1.0.0"
    valid: bool = True
    reason: str = "Complies with verified generation policy"

class ExecutionPermit(BaseModel):
    """Single-use authorization token required by Plane D action service."""
    permit_id: str
    receipt_id: str
    request_id: str
    policy_generation: int
    effect_hash: str
    issued_at: datetime
    expires_at: datetime
    kernel_signature: str

class FenceEvaluationResult(BaseModel):
    """Result of evaluating an action proposal against the generation fence."""
    allowed: bool
    status: str # "PERMITTED" | "FENCE_BLOCKED" | "POLICY_VIOLATION" | "EXPIRED"
    reason: str
    current_generation: int
    proposed_generation: int
    receipt: Optional[AuthorityReceipt] = None
    snapshot: Optional[AuthoritySnapshot] = None

class CommitResult(BaseModel):
    """Final output of Two-Phase Commit Gate."""
    committed: bool
    status: str # "COMMITTED" | "ABORTED_STALE_GENERATION" | "ABORTED_TAMPER" | "ABORTED_EXPIRED"
    permit: Optional[ExecutionPermit] = None
    effect_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    audit_trail: Dict[str, Any] = Field(default_factory=dict)
