"""Runs the controlled causal benchmark."""

import sys
import subprocess
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent
    cmd = [sys.executable, str(root / "benchmarks" / "campaign.py")]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
