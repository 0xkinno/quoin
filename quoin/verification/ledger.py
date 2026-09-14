"""Verification and telemetry ledger for receipts and fence evaluations."""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from ..kernel.models import AuthorityReceipt, FenceEvaluationResult, CommitResult

class VerificationLedger:
    """Audit ledger tracking all authority transactions, receipts, and outcomes."""

    def __init__(self):
        self._receipts: Dict[str, AuthorityReceipt] = {}
        self._evaluations: List[FenceEvaluationResult] = []
        self._commits: List[CommitResult] = []

    def record_receipt(self, receipt: AuthorityReceipt) -> None:
        self._receipts[receipt.receipt_id] = receipt

    def record_evaluation(self, evaluation: FenceEvaluationResult) -> None:
        self._evaluations.append(evaluation)
        if evaluation.receipt:
            self._receipts[evaluation.receipt.receipt_id] = evaluation.receipt

    def record_commit(self, commit: CommitResult) -> None:
        self._commits.append(commit)

    def get_receipt(self, receipt_id: str) -> Optional[AuthorityReceipt]:
        return self._receipts.get(receipt_id)

    def get_all_receipts(self) -> List[AuthorityReceipt]:
        return list(self._receipts.values())

    def get_all_evaluations(self) -> List[FenceEvaluationResult]:
        return list(self._evaluations)

    def get_all_commits(self) -> List[CommitResult]:
        return list(self._commits)

    def stats(self) -> Dict[str, int]:
        total_evals = len(self._evaluations)
        blocked = sum(1 for e in self._evaluations if not e.allowed)
        permitted = sum(1 for e in self._evaluations if e.allowed)
        committed = sum(1 for c in self._commits if c.committed)
        aborted = sum(1 for c in self._commits if not c.committed)
        return {
            "total_evaluations": total_evals,
            "fence_blocked": blocked,
            "permitted": permitted,
            "total_commits": len(self._commits),
            "committed_effects": committed,
            "aborted_commits": aborted,
            "active_receipts": len(self._receipts),
        }
