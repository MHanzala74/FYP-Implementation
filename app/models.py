"""
ASTRA - Model Loading (Singleton Pattern)
Models are loaded once from the artifacts folder, not on every request.
"""

import os
import joblib
import numpy as np
from pathlib import Path

# ─── Artifacts path ─────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
ARTIFACTS  = BASE_DIR / "artifacts"

# ─── 51 Features (exact order from training notebook) ──────────────────────────
EXPECTED_COLS = [
    "Flow_Duration", "Total_Fwd_Packets", "Total_Length_of_Fwd_Packets",
    "Fwd_Packet_Length_Max", "Fwd_Packet_Length_Min", "Fwd_Packet_Length_Mean",
    "Bwd_Packet_Length_Max", "Bwd_Packet_Length_Min", "Flow_Bytes/s", "Flow_Packets/s",
    "Flow_IAT_Mean", "Flow_IAT_Std", "Flow_IAT_Max", "Flow_IAT_Min", "Fwd_IAT_Mean",
    "Fwd_IAT_Std", "Fwd_IAT_Min", "Bwd_IAT_Total", "Bwd_IAT_Mean", "Bwd_IAT_Std",
    "Bwd_IAT_Max", "Bwd_IAT_Min", "Fwd_PSH_Flags", "Fwd_Header_Length",
    "Bwd_Header_Length", "Bwd_Packets/s", "Min_Packet_Length", "Max_Packet_Length",
    "Packet_Length_Mean", "Packet_Length_Variance", "FIN_Flag_Count", "RST_Flag_Count",
    "PSH_Flag_Count", "ACK_Flag_Count", "URG_Flag_Count", "Down/Up_Ratio",
    "Fwd_Avg_Bytes/Bulk", "Fwd_Avg_Packets/Bulk", "Fwd_Avg_Bulk_Rate",
    "Bwd_Avg_Bytes/Bulk", "Bwd_Avg_Packets/Bulk", "Bwd_Avg_Bulk_Rate",
    "Init_Win_bytes_forward", "Init_Win_bytes_backward", "act_data_pkt_fwd",
    "min_seg_size_forward", "Active_Mean", "Active_Std", "Active_Max",
    "Active_Min", "Idle_Std",
]

# ─── Class labels ───────────────────────────────────────────────────────────────
THREAT_LABELS = ["benign", "bruteforce", "ddos", "dos", "infiltration", "portscan"]

# ─── Severity mapping ───────────────────────────────────────────────────────────
SEVERITY_MAP = {
    "benign":       "none",
    "bruteforce":   "high",
    "ddos":         "critical",
    "dos":          "critical",
    "infiltration": "high",
    "portscan":     "medium",
}

# ─── Recommended actions ────────────────────────────────────────────────────────
RESPONSE_MAP = {
    "benign":       "No action required.",
    "bruteforce":   "Block source IP. Enable account lockout policy.",
    "ddos":         "Activate DDoS mitigation. Rate-limit source. Alert NOC.",
    "dos":          "Rate-limit traffic. Block offending IP. Alert security team.",
    "infiltration": "Isolate affected system. Conduct forensic analysis.",
    "portscan":     "Flag source IP for monitoring. Review firewall rules.",
}


class ModelManager:
    """Singleton - models are loaded only once at app startup."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def load(self):
        if self._loaded:
            return

        self.rf      = joblib.load(ARTIFACTS / "rf_multiclass.pkl")
        self.xgb     = joblib.load(ARTIFACTS / "xgb_multiclass.pkl")
        self.le      = joblib.load(ARTIFACTS / "label_encoder.pkl")
        self.scaler  = joblib.load(ARTIFACTS / "scaler.pkl")
        self._loaded = True

    def is_ready(self) -> bool:
        return self._loaded

    def predict(self, X_scaled: np.ndarray) -> dict:
        """
        Returns RF and XGBoost predictions for a scaled numpy array.
        X_scaled shape: (n_samples, 51)
        """
        rf_enc  = self.rf.predict(X_scaled)
        xgb_enc = self.xgb.predict(X_scaled)

        rf_labels  = self.le.inverse_transform(rf_enc).tolist()
        xgb_labels = self.le.inverse_transform(xgb_enc).tolist()

        # Probability scores (RF supports predict_proba)
        rf_proba  = self.rf.predict_proba(X_scaled).max(axis=1).tolist()
        xgb_proba = self.xgb.predict_proba(X_scaled).max(axis=1).tolist()

        return {
            "rf_predictions":   rf_labels,
            "xgb_predictions":  xgb_labels,
            "rf_confidence":    rf_proba,
            "xgb_confidence":   xgb_proba,
        }


# ─── Global singleton ───────────────────────────────────────────────────────────
model_manager = ModelManager()