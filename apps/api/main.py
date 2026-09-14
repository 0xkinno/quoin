"""QUOIN FastAPI Backend Service.

Exposes live policy cutover, two-phase authority gates, AgentCore memory telemetry, Break It lab, and proof center.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import policies, requests, memory, lab, proof

app = FastAPI(
    title="QUOIN API",
    description="Deterministic Policy-Generation Fence Backend Service",
    version="1.0.0",
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    return {
        "status": "HEALTHY",
        "service": "quoin-backend",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)
