import os
import time
from pathlib import Path
from dotenv import dotenv_values
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import policies, requests, memory, lab, proof, trace

START_TIME = time.time()

env_path = Path(__file__).resolve().parent.parent.parent / ".env.local"
env_cfg = dotenv_values(env_path) if env_path.exists() else {}

cors_env = os.environ.get("CORS_ORIGINS") or env_cfg.get("CORS_ORIGINS", "*")
allow_origins = [o.strip() for o in cors_env.split(",") if o.strip()] if cors_env != "*" else ["*"]

app = FastAPI(
    title="QUOIN API",
    description="Deterministic Policy-Generation Fence Backend Service",
    version="1.0.0",
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(policies.router)
app.include_router(requests.router)
app.include_router(memory.router)
app.include_router(lab.router)
app.include_router(proof.router)
app.include_router(trace.router)

@app.get("/")
def root():
    return {
        "service": "QUOIN Authority Fence Service",
        "version": "1.0.0",
        "status": "OPERATIONAL",
        "invariant": "No action executes without verified generation receipt."
    }

@app.get("/api/health")
def health():
    uptime = round(time.time() - START_TIME, 2)
    use_dynamo = bool(env_cfg.get("DYNAMODB_TABLE_NAME") and env_cfg.get("AWS_ACCESS_KEY_ID"))
    return {
        "status": "HEALTHY",
        "service": "quoin-backend",
        "version": "1.0.0",
        "uptime_seconds": uptime,
        "authority_ledger": "dynamodb" if use_dynamo else "sqlite_wal_durable",
        "memory_source": "local_simulator",
        "planes_active": [
            "Plane A: Strands Reasoning Agent (Amazon Bedrock Nova Lite)",
            "Plane B: Deterministic Kernel Fence & Read-After-Write CAS Gate",
            "Plane C: Cognitive Memory & Policy Ledger",
            "Plane D: Operational Action Service & Idempotency Engine"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)
