"""Runs the empirical research campaign on memory visibility."""

import sys
import subprocess
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent
    cmd = [sys.executable, str(root / "research" / "experiments" / "memory_visibility" / "campaign.py")]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
