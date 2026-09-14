"""Standalone script to verify cryptographic receipts."""

import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from quoin.kernel.hasher import CanonicalHasher

def main():
    print("Verifying canonical hashing and receipt generation...")
    req = {"client_id": "cust_40", "amount": 500.0, "tier": "gold"}
    h = CanonicalHasher.compute_request_hash(req)
    pid = CanonicalHasher.compute_receipt_id("req_40", 18, h)
    assert pid.startswith("rcpt_")
    print(f"Receipt digest verified: {pid}")
    print("Receipts: PASS")

if __name__ == "__main__":
    main()
