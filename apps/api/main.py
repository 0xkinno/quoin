import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from quoin.config import get_config
from .routes import policies, requests, memory, lab, proof, trace

START_TIME = time.time()

cors_env = get_config("CORS_ORIGINS", "*")
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
    from .state import app_state
    uptime = round(time.time() - START_TIME, 2)
    mem_status = app_state.memory.status()
    auth_status = app_state.authority_ledger.status()
    return {
        "status": "HEALTHY",
        "service": "quoin-backend",
        "version": "1.0.0",
        "uptime_seconds": uptime,
        "authority_ledger": auth_status["active_storage"],
        "authority_table": auth_status["table_name"],
        "memory_source": mem_status["source"],
        "memory_mode": mem_status["mode"],
        "memory_id": mem_status["memory_id"],
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
