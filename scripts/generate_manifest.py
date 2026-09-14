import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent.parent

files_to_hash = [
    root / "evidence" / "traces" / "attack_results.json",
    root / "evidence" / "benchmark" / "results.json",
    root / "docs" / "FINDING.md",
    root / "docs" / "RESULTS.md",
    root / "docs" / "THREAT_MODEL.md",
    root / "docs" / "PROOF.md",
]

entries = []
for p in files_to_hash:
    if p.exists():
        content = p.read_bytes()
        entries.append({
            "path": str(p.relative_to(root)).replace("\\", "/"),
            "size_bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest()
        })

manifest = {
    "project": "QUOIN",
    "version": "1.0.0",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "manifest_version": "1.0",
    "artifacts": entries
}

manifest_path = root / "evidence" / "manifests" / "manifest.json"
manifest_path.parent.mkdir(parents=True, exist_ok=True)
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(f"Generated evidence manifest: {manifest_path} with {len(entries)} artifacts.")
