from fastapi import APIRouter, HTTPException
import json
from pathlib import Path

router = APIRouter(prefix="/api/lab", tags=["Lab"])

root = Path(__file__).resolve().parent.parent.parent.parent

@router.get("/scenarios")
def get_lab_scenarios():
    trace_path = root / "evidence" / "traces" / "attack_results.json"
    if trace_path.exists():
        with open(trace_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    # Fallback to direct definitions if file not yet generated
    return {"total_attacks": 13, "traces": []}

@router.post("/run/{attack_id}")
def run_single_attack(attack_id: str):
    trace_path = root / "evidence" / "traces" / "attack_results.json"
    if not trace_path.exists():
        raise HTTPException(status_code=404, detail="Attack traces not found")
    with open(trace_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for t in data.get("traces", []):
        if t["id"].lower() == attack_id.lower() or t["id"].replace("ATT_", "").lower() == attack_id.lower():
            return {"status": "SUCCESS", "attack": t}
    raise HTTPException(status_code=404, detail=f"Attack ID {attack_id} not found")
