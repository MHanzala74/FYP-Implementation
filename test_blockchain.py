"""
ASTRA — Blockchain Direct Test
Tests blockchain directly without FastAPI.
Run: python test_blockchain.py
"""

import os
import json
from pathlib import Path
from web3 import Web3

# ── Config ──────────────────────────────────────────────────────────
GANACHE_URL      = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "0x86D2fbd3528866f2Ac2CA84dc42D716dF20882d7")   # or paste directly here
ABI_PATH         = Path("app/ThreatLog_abi.json")

# If env variable is not set, paste directly here:
if not CONTRACT_ADDRESS:
    CONTRACT_ADDRESS = "0x86D2fbd3528866f2Ac2CA84dc42D716dF20882d7"  # your address

print("=" * 55)
print("  ASTRA — Blockchain Direct Test")
print("=" * 55)

# 1. Connect
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
print(f"Connected: {w3.is_connected()}")
print(f"Account  : {w3.eth.accounts[0]}")
print(f"Contract : {CONTRACT_ADDRESS}")

# 2. Load ABI
if not ABI_PATH.exists():
    print(f"❌ ABI file not found: {ABI_PATH}")
    print("   Try: app/ThreatLog_abi.json")
    exit(1)

abi = json.loads(ABI_PATH.read_text())
addr = Web3.to_checksum_address(CONTRACT_ADDRESS)
contract = w3.eth.contract(address=addr, abi=abi)

# 3. Check total records
try:
    total = contract.functions.getTotalRecords().call()
    print(f"\n✅ getTotalRecords() = {total}")
except Exception as e:
    print(f"\n❌ getTotalRecords() FAILED: {e}")
    exit(1)

# 4. Log directly
print("\n⏳ Logging test threat...")
try:
    account = w3.eth.accounts[0]
    tx = contract.functions.logThreat(
        "dos",          # threatType
        "critical",     # severity
        "dos",          # rfPrediction
        "dos",          # xgbPrediction
        10000,          # rfConfidence (100.00%)
        9994,           # xgbConfidence (99.94%)
        "Block IP.",    # recommendedAction
        True            # isThreat
    ).transact({"from": account, "gas": 500_000})

    receipt = w3.eth.wait_for_transaction_receipt(tx)
    print(f"✅ Log success! Tx: {tx.hex()[:30]}...")
    print(f"   Block: {receipt['blockNumber']}, Gas: {receipt['gasUsed']}")
except Exception as e:
    print(f"❌ logThreat() FAILED: {e}")
    exit(1)

# 5. Read record back
try:
    total2 = contract.functions.getTotalRecords().call()
    print(f"\n✅ Total records now: {total2}")

    rec = contract.functions.getRecord(0).call()
    print(f"   Record[0]: type={rec[1]}, severity={rec[2]}, threat={rec[8]}")
except Exception as e:
    print(f"❌ getRecord() FAILED: {e}")

print("\n" + "=" * 55)
print("  Test complete!")
print("=" * 55)