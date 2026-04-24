"""
ASTRA - Application Startup
Load models when the app starts.
"""

from app.main import app
from app.models import model_manager
from app.blockchain import blockchain


@app.on_event("startup")
async def startup_event():
    print("🚀 ASTRA starting up...")

    try:
        model_manager.load()
        print("✅ ML Models loaded successfully!")
    except FileNotFoundError as e:
        print(f"⚠️ Warning: Model files not found: {e}")

    # Blockchain connect (optional — if Ganache is not running, skip gracefully)
    blockchain.connect()