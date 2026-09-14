"""Standalone script to verify generation fences and commit gate invariants."""

import sys
import subprocess
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent
    cmd = [sys.executable, "-m", "pytest", str(root / "tests" / "adversarial" / "test_break_campaign.py"), "-v"]
    print("Running 13-attack adversarial invariant validation...")
    res = subprocess.run(cmd)
    if res.returncode == 0:
        print("\nAll 13 Invariant Attacks Defeated: PASS")
        sys.exit(0)
    else:
        print("\nInvariant Violation Detected: FAIL")
        sys.exit(1)

if __name__ == "__main__":
    main()
