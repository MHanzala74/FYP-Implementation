"""
ASTRA - AI-Based Cyber Threat Detection and Response System
FastAPI Backend - Main Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import predict, health, batch, blockchain_router

app = FastAPI(
    title="ASTRA - Cyber Threat Detection API",
    description=(
        "AI-Based Cyber Threat Detection and Response System. "
        "Detects threats like DoS, DDoS, BruteForce, PortScan using ML models."
    ),
    version="1.0.0",
)

# ─── CORS (for React dashboard) ────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # In production, use your dashboard URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router,              prefix="/api/v1", tags=["Health"])
app.include_router(predict.router,             prefix="/api/v1", tags=["Prediction"])
app.include_router(batch.router,               prefix="/api/v1", tags=["Batch Prediction"])
app.include_router(blockchain_router.router,   prefix="/api/v1", tags=["Blockchain"])


@app.get("/", tags=["Root"])
def root():
    return {
        "project": "ASTRA",
        "description": "AI-Based Cyber Threat Detection and Response System",
        "docs": "/docs",
        "version": "1.0.0",
    }