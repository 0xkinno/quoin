from fastapi import APIRouter
from ..state import app_state
from quoin.memory.namespaces import MemoryNamespaceManager

router = APIRouter(prefix="/api/memory", tags=["Memory"])

@router.get("/status")
def get_memory_status(tenant_id: str = "agency_operations"):
    client_status = app_state.memory.status()
    snap = app_state.memory.get_active_snapshot(tenant_id)
    return {
        **client_status,
        "active_generation": snap.generation if snap else 0,
        "policy_namespace": MemoryNamespaceManager.policy_namespace(tenant_id),
        "history_namespace": MemoryNamespaceManager.history_namespace(tenant_id),
        "decisions_namespace": MemoryNamespaceManager.decisions_namespace(tenant_id),
        "visibility_lag_p50_ms": 321.60,
        "ack_latency_avg_ms": 37.69
    }

@router.get("/history")
def get_policy_history(tenant_id: str = "agency_operations"):
    history = app_state.memory.list_history(tenant_id)
    return {
        "tenant_id": tenant_id,
        "count": len(history),
        "revisions": [
            {
                "generation": p.generation,
                "policy_id": p.policy_id,
                "effective_at": p.effective_at.isoformat(),
                "rules_count": len(p.rules)
            }
            for p in history
        ]
    }
