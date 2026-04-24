import io
import numpy as np
import pandas as pd
from collections import Counter
from fastapi import APIRouter, HTTPException, UploadFile, File

from app.schemas import NetworkFlow, ThreatPrediction, BatchRequest, BatchPrediction
from app.models import model_manager, EXPECTED_COLS, SEVERITY_MAP, RESPONSE_MAP
from app.routers.predict import flow_to_array, make_verdict
from app.blockchain import blockchain

router = APIRouter()


def build_predictions(X_scaled: np.ndarray) -> list[ThreatPrediction]:
    result = model_manager.predict(X_scaled)
    preds = []
    for i in range(len(result["rf_predictions"])):
        rf_label = result["rf_predictions"][i]
        xgb_label = result["xgb_predictions"][i]
        verdict = make_verdict(rf_label, xgb_label)

        preds.append(ThreatPrediction(
            rf_prediction=rf_label,
            xgb_prediction=xgb_label,
            rf_confidence=round(result["rf_confidence"][i], 4),
            xgb_confidence=round(result["xgb_confidence"][i], 4),
            final_verdict=verdict,
            severity=SEVERITY_MAP.get(verdict, "unknown"),
            recommended_action=RESPONSE_MAP.get(verdict, "Investigate manually."),
            is_threat=(verdict != "benign"),
        ))
    return preds


def log_threats_to_blockchain(preds: list[ThreatPrediction]):
    """Log only threats to the blockchain (skip benign)."""
    logged = 0
    for p in preds:
        if p.is_threat:
            tx = blockchain.log_threat(p.model_dump())
            if tx:
                logged += 1

    if logged:
        print(f"⛓ Blockchain: {logged} threat(s) logged.")


# ─── JSON batch ──────────────────────────────────────────────────────
@router.post("/predict/batch", response_model=BatchPrediction)
def predict_batch(request: BatchRequest):
    """Analyze multiple network flows together (JSON body). Max 1000."""
    
    if not model_manager.is_ready():
        raise HTTPException(status_code=503, detail="Models are not loaded yet.")

    if len(request.flows) > 1000:
        raise HTTPException(status_code=400, detail="Max 1000 flows per request.")

    X = np.vstack([flow_to_array(f) for f in request.flows])
    X_scaled = model_manager.scaler.transform(X)
    preds = build_predictions(X_scaled)

    # ── Blockchain logging ──────────────────────────────────────────
    log_threats_to_blockchain(preds)

    summary = dict(Counter(p.final_verdict for p in preds))

    return BatchPrediction(
        total_flows=len(preds),
        threats_found=sum(1 for p in preds if p.is_threat),
        results=preds,
        summary=summary,
    )


# ─── CSV upload ──────────────────────────────────────────────────────
@router.post("/predict/csv", response_model=BatchPrediction)
async def predict_csv(file: UploadFile = File(...)):
    """Upload a CSV file and get batch predictions. Max 5000 rows."""

    if not model_manager.is_ready():
        raise HTTPException(status_code=503, detail="Models are not loaded yet.")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are allowed.")

    contents = await file.read()

    try:
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV parse error: {e}")

    if len(df) > 5000:
        raise HTTPException(status_code=400, detail="Max 5000 rows per CSV.")

    df.columns = df.columns.str.strip()
    df = df.reindex(columns=EXPECTED_COLS, fill_value=0.0).fillna(0.0)

    try:
        X_scaled = model_manager.scaler.transform(df.values.astype(np.float64))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Scaling error: {e}")

    preds = build_predictions(X_scaled)

    # ── Blockchain logging ──────────────────────────────────────────
    log_threats_to_blockchain(preds)

    summary = dict(Counter(p.final_verdict for p in preds))

    return BatchPrediction(
        total_flows=len(preds),
        threats_found=sum(1 for p in preds if p.is_threat),
        results=preds,
        summary=summary,
    )