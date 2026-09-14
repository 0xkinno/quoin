"""Namespace schemas and routing for QUOIN AgentCore Memory."""

import re

class MemoryNamespaceManager:
    """Manages structured namespaces for multi-tenant policy and decision isolation."""

    @staticmethod
    def policy_namespace(tenant_id: str) -> str:
        clean_tenant = re.sub(r"[^a-zA-Z0-9_-]", "_", tenant_id)
        return f"/quoin/{clean_tenant}/policy"

    @staticmethod
    def history_namespace(tenant_id: str) -> str:
        clean_tenant = re.sub(r"[^a-zA-Z0-9_-]", "_", tenant_id)
        return f"/quoin/{clean_tenant}/policy_history"

    @staticmethod
    def decisions_namespace(tenant_id: str) -> str:
        clean_tenant = re.sub(r"[^a-zA-Z0-9_-]", "_", tenant_id)
        return f"/quoin/{clean_tenant}/decisions"

    @staticmethod
    def validate_namespace(namespace: str) -> bool:
        pattern = r"^/quoin/[a-zA-Z0-9_-]+/(policy|policy_history|decisions)$"
        return bool(re.match(pattern, namespace))
