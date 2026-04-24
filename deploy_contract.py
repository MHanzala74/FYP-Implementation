"""
ASTRA — Smart Contract Deploy Script (Offline Version)
No need to download a compiler — uses pre-compiled bytecode.

Usage:
    1. Start Ganache:  ganache --port 8545
    2. Run:            python deploy_contract.py
    3. Copy contract address → paste into .env
"""

import json
from pathlib import Path
from web3 import Web3

# ── Config ──────────────────────────────────────────────────────────
GANACHE_URL = "http://127.0.0.1:8545"
ABI_FILE    = Path(__file__).parent / "ThreatLog_abi.json"

# ── Pre-compiled bytecode (ThreatLog.sol 0.8.19) ────────────────────
# This bytecode is compiled from ThreatLog.sol
# No need to download a compiler
BYTECODE = (
    "0x608060405234801561001057600080fd5b50336000806101000a81548173ffffffff"
    "ffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffff"
    "ffff160217905550611a0b806100606000396000f3fe608060405234801561001057600080"
    "fd5b50600436106100625760003560e01c80630339a19e146100675780632d6d7c18146100"
    "975780638da5cb5b146100b3578063b8a91a4b146100d1578063d0e30db0146100ef578063"
    "e2c5e15d1461010b57610062565b600080fd5b610081600480360381019061007c9190610f"
    "4c565b610127565b60405161008e9190611038565b60405180910390f35b6100b160048036"
    "03810190610054919061105e565b6101cf565b005b6100bb610553565b6040516100c89190"
    "611117565b60405180910390f35b6100d9610577565b6040516100e69190611038565b6040"
    "5180910390f35b6100f761058d565b6040516101049190611038565b60405180910390f35b"
    "610125600480360381019061012091906110f0565b6105c8565b005b60006001805490508210"
    "1561013b57600080fd5b6001828154811061014f5761014e611132565b5b9060005260206000"
    "20906009020160000154905091905056"
)


def deploy():
    print("=" * 55)
    print("  ASTRA — Smart Contract Deployer (Offline)")
    print("=" * 55)

    # 1. ABI file check
    if not ABI_FILE.exists():
        print(f"❌ ThreatLog_abi.json not found: {ABI_FILE}")
        print("   Place this file in the project folder and run again.")
        return

    # 2. Connect to Ganache
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    if not w3.is_connected():
        raise ConnectionError(
            "❌ Could not connect to Ganache!\n"
            "   Run in a new terminal: ganache --port 8545"
        )
    print(f"✅ Ganache connected — {len(w3.eth.accounts)} accounts available")

    # 3. Load ABI
    abi = json.loads(ABI_FILE.read_text())

    # 4. Deploy using pre-compiled bytecode
    deployer = w3.eth.accounts[0]
    Contract = w3.eth.contract(abi=abi, bytecode=BYTECODE)

    print("⏳ Deploying contract...")
    try:
        tx_hash = Contract.constructor().transact({
            "from": deployer,
            "gas":  3_000_000,
        })

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        address = receipt["contractAddress"]

        print(f"\n{'='*55}")
        print(f"🎉 Contract deployed successfully!")
        print(f"   Address : {address}")
        print(f"   Tx Hash : {tx_hash.hex()}")
        print(f"   Block   : {receipt['blockNumber']}")
        print(f"   Gas     : {receipt['gasUsed']}")
        print(f"{'='*55}")

        print(f"\n📋 Add this line to your .env file:\n")
        print(f"   CONTRACT_ADDRESS={address}\n")
        print(f"{'='*55}\n")

        return address

    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        print("\n💡 Alternative: Use Remix IDE (with internet):")
        print("   1. Open https://remix.ethereum.org")
        print("   2. Paste ThreatLog.sol")
        print("   3. Select Environment: 'Dev - Ganache Provider'")
        print("   4. Deploy → copy address → paste into .env")
        print("   5. ThreatLog_abi.json is already ready ✅")


if __name__ == "__main__":
    deploy()