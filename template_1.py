import os
from pathlib import Path

project_name = ""

list_of_files = [

    # ── FastAPI App ───────────────────────────────────────────────
    f"__init__.py",
    f"main.py",           # FastAPI entry point
    f"routes.py",         # API endpoints
    f"schema.py",         # Pydantic models

    # ── Source: Data ──────────────────────────────────────────────
    f"src/__init__.py",
    f"src/data/__init__.py",
    f"src/data/ingestion.py",      # Load dataset
    f"src/data/preprocessing.py",  # Cleaning, encoding, scaling

    # ── Source: Features ──────────────────────────────────────────
    f"src/features/__init__.py",
    f"src/features/feature_engineering.py",
    f"src/features/feature_selection.py",
    
    f"src/logger/__init__.py",
    f"src/exception/__init__.py",

    # ── Source: Model ─────────────────────────────────────────────
    f"src/model/__init__.py",
    f"src/model/cnn_model.py",  # CNN architecture
    f"src/model/train.py",      # Training logic
    f"src/model/evaluate.py",   # Accuracy, metrics
    f"src/model/predict.py",    # Inference logic

    # ── Source: Pipeline ──────────────────────────────────────────
    f"src/pipeline/__init__.py",
    f"src/pipeline/training_pipeline.py",
    f"src/pipeline/prediction_pipeline.py",

    # ── Source: Utils ─────────────────────────────────────────────
    f"src/utils/__init__.py",
    f"src/utils/logger.py",     # Logging setup
    f"src/utils/exception.py",  # Custom exception
    f"src/utils/common.py",     # Helper functions

    # ── Artifacts (gitignored) ────────────────────────────────────
    f"artifacts/.gitkeep",      # model.pkl, scaler.pkl, encoder.pkl

    # ── Logs (gitignored) ─────────────────────────────────────────
    f"logs/.gitkeep",           # app.log

    # ── Notebooks ─────────────────────────────────────────────────
    f"notebooks/.gitkeep",      # existing FYP notebooks yahan rakho

    # ── Root Level Files ──────────────────────────────────────────
    f"requirements.txt",
    f"config.yaml",             # paths, hyperparams, settings
    f"Dockerfile",              # optional (bonus points)
    
]



# ── Main Loop ─────────────────────────────────────────────────────

for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    if filedir != "":
        os.makedirs(filedir, exist_ok=True)

    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, "w") as f:
            pass
        print(f"  ✅ {filepath}")
    else:
        print(f"  ⚠️  Already exists: {filepath}")

# ── Files with starter content ────────────────────────────────────
root = Path(project_name)







print(f"\n🎉 '{project_name}' successfully create ho gaya!")
print(f"📂 Next step:  cd {project_name}\n")
