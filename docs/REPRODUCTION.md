# QUOIN Terminal Reproduction Guide

Anyone can clone and verify the entire QUOIN system directly from the terminal without requiring cloud credentials or web setup.

## 1. Prerequisites
- Python 3.10+
- `uv` (or `pip`)
- Git

## 2. Setup Environment
```bash
# Clone repository
git clone <repo-url>
cd QUOIN

# Create virtual environment
uv venv .venv
# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

## 3. Run the Master Verifier
Verify all cryptographic receipts, generation fences, tamper detection, and benchmark manifests in a single command:
```bash
python scripts/verify_all.py
```

## 4. Run the Full Test Suite
```bash
pytest tests/ -v
```

## 5. Run the 13-Class Adversarial Attack Campaign
```bash
python scripts/run_break_campaign.py
```

## 6. Run the Controlled Comparative Benchmark
```bash
python benchmarks/campaign.py
```

## 7. Run the AgentCore Memory Visibility Experiment
```bash
python research/experiments/memory_visibility/campaign.py
```
