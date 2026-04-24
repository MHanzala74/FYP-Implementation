"""
ASTRA — Blockchain Integration Module
Handles Web3 calls inside FastAPI.
Logs every detected threat to the blockchain.
"""

import json
import os
from pathlib import Path
from typing import Optional
from web3 import Web3
from web3.exceptions import ContractLogicError
from dotenv import load_dotenv

load_dotenv()

# ── Config (from environment variables) ───────────────────────────────
GANACHE_URL       = os.getenv("GANACHE_URL",       "http://127.0.0.1:8545")
CONTRACT_ADDRESS  = os.getenv("CONTRACT_ADDRESS",  "")   # fill after deployment
ABI_PATH          = Path(__file__).parent / "ThreatLog_abi.json"


class BlockchainLogger:
    """
    Singleton — connect once, reuse multiple times.
    If Ganache is not running, it will fail gracefully (API will not crash).
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._ready = False
        return cls._instance

    def connect(self):
        """Call this at FastAPI startup."""
        if self._ready:
            return

        if not CONTRACT_ADDRESS:
            print("⚠️  Blockchain: CONTRACT_ADDRESS is missing in .env — logging disabled.")
            return

        if not ABI_PATH.exists():
            print("⚠️  Blockchain: ThreatLog_abi.json not found — run deploy_contract.py first.")
            return

        try:
            self._w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

            if not self._w3.is_connected():
                print("⚠️  Blockchain: Could not connect to Ganache — logging disabled.")
                return

            abi = json.loads(ABI_PATH.read_text())
            checksum_addr = Web3.to_checksum_address(CONTRACT_ADDRESS)

            self._contract  = self._w3.eth.contract(address=checksum_addr, abi=abi)
            self._account   = self._w3.eth.accounts[0]   # default Ganache account
            self._ready     = True

            print(f"✅ Blockchain connected: {GANACHE_URL}")
            print(f"   Contract : {checksum_addr}")
            print(f"   Account  : {self._account}")

        except Exception as e:
            print(f"⚠️  Blockchain init error: {e} — logging disabled.")

    def is_ready(self) -> bool:
        return self._ready

    def log_threat(self, prediction: dict) -> Optional[str]:
        """
        Store a threat prediction on the blockchain.

        Args:
            prediction: response dict from /predict endpoint

        Returns:
            tx_hash string if success, None if failed
        """
        if not self._ready:
            return None

        try:
            # Convert confidence 0–1 float → integer (e.g. 0.9876 → 9876)
            rf_conf  = int(prediction.get("rf_confidence",  0) * 10_000)
            xgb_conf = int(prediction.get("xgb_confidence", 0) * 10_000)

            tx_hash = self._contract.functions.logThreat(
                prediction.get("final_verdict",      "unknown"),
                prediction.get("severity",           "unknown"),
                prediction.get("rf_prediction",      "unknown"),
                prediction.get("xgb_prediction",     "unknown"),
                rf_conf,
                xgb_conf,
                prediction.get("recommended_action", ""),
                bool(prediction.get("is_threat",     False)),
            ).transact({
                "from": self._account,
                "gas":  500_000,
            })

            receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash)
            tx_str  = tx_hash.hex()

            print(f"⛓ Blockchain log: {tx_str[:20]}... block={receipt['blockNumber']}")
            return tx_str

        except ContractLogicError as e:
            print(f"⚠️  Contract error: {e}")
            return None
        except Exception as e:
            print(f"⚠️  Blockchain log error: {e}")
            return None

    def get_all_logs(self) -> list[dict]:
        """Fetch all threat records from the blockchain."""
        if not self._ready:
            return []

        try:
            total = self._contract.functions.getTotalRecords().call()
            logs  = []

            for i in range(total):
                rec = self._contract.functions.getRecord(i).call()
                logs.append({
                    "record_id":          i,
                    "timestamp":          rec[0],
                    "threat_type":        rec[1],
                    "severity":           rec[2],
                    "rf_prediction":      rec[3],
                    "xgb_prediction":     rec[4],
                    "rf_confidence":      rec[5] / 10_000,
                    "xgb_confidence":     rec[6] / 10_000,
                    "recommended_action": rec[7],
                    "is_threat":          rec[8],
                })

            return logs

        except Exception as e:
            print(f"⚠️  Blockchain read error: {e}")
            return []

    def get_stats(self) -> dict:
        """Get summary stats from the blockchain."""
        if not self._ready:
            return {"enabled": False}

        try:
            total   = self._contract.functions.getTotalRecords().call()
            threats = self._contract.functions.getThreatCount().call()

            return {
                "enabled":       True,
                "total_records": total,
                "threat_count":  threats,
                "benign_count":  total - threats,
                "contract":      CONTRACT_ADDRESS,
                "node":          GANACHE_URL,
            }

        except Exception as e:
            return {"enabled": False, "error": str(e)}


# ── Global singleton ─────────────────────────────────────────────────
blockchain = BlockchainLogger()