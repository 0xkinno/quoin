"""Central configuration reader for QUOIN.

Reads configuration prioritizing:
1. Environment variables (os.environ) injected by host/PaaS (Render, Docker, Kubernetes, AWS)
2. Local overrides from .env.local
3. Project defaults from .env
4. Safe fallback defaults
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import dotenv_values

_ROOT_DIR = Path(__file__).resolve().parent.parent

_env_local_path = _ROOT_DIR / ".env.local"
_env_path = _ROOT_DIR / ".env"

_env_local_cfg: Dict[str, Optional[str]] = dotenv_values(_env_local_path) if _env_local_path.exists() else {}
_env_cfg: Dict[str, Optional[str]] = dotenv_values(_env_path) if _env_path.exists() else {}

def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve configuration value by key with priority:
    1. os.environ (injected by host/PaaS e.g. Render, Docker, ECS)
    2. .env.local (local development overrides)
    3. .env (standard project defaults)
    4. default fallback value
    """
    val = os.environ.get(key)
    if val is not None and val.strip() != "":
        return val.strip()
    
    val = _env_local_cfg.get(key)
    if val is not None and str(val).strip() != "":
        return str(val).strip()

    val = _env_cfg.get(key)
    if val is not None and str(val).strip() != "":
        return str(val).strip()

    return default

def get_quoin_mode() -> str:
    """Resolve active QUOIN execution mode ('local' vs 'agentcore').
    
    Priority:
    1. Explicit QUOIN_MODE from environment variable or .env.local/.env
    2. Auto-detection: If AWS credentials and AGENTCORE_MEMORY_ID are present, default to 'agentcore'.
    3. Safe default: 'local' (offline reproducible simulation mode)
    """
    explicit = get_config("QUOIN_MODE")
    if explicit:
        return explicit.lower()

    # Auto-detection: if live AWS credentials and memory ID are configured, use agentcore
    has_aws = bool(
        get_config("AWS_ACCESS_KEY_ID")
        and get_config("AWS_SECRET_ACCESS_KEY")
        and get_config("AGENTCORE_MEMORY_ID")
    )
    return "agentcore" if has_aws else "local"
