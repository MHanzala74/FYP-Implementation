# Network Intrusion Detection System (NIDS)

A Machine Learning-based Network Intrusion Detection System that classifies network traffic as normal or malicious, with blockchain integration for secure threat logging.

## Overview

This project implements a Machine Learning-based Network Intrusion Detection System to classify network traffic as either normal or malicious. The system leverages advanced ML algorithms to detect cyber threats in real-time and maintains an immutable audit trail of detected threats using blockchain technology.

## Key Features

- **Intrusion Detection**: Classifies network traffic into normal or attack categories using ML models
- **Multiple ML Models**: Supports various classifiers including XGBoost for accurate threat detection
- **Real-time Prediction**: API-based inference for live traffic analysis
- **Blockchain Integration**: Secure, tamper-proof logging of detected threats via smart contracts
- **RESTful API**: FastAPI backend with endpoints for model training and prediction
- **Data Preprocessing**: Automated feature scaling and handling of imbalanced datasets

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI, Python 3.12 |
| **ML Framework** | scikit-learn, XGBoost, pandas, numpy |
| **Blockchain** | Web3.py, Solidity Smart Contracts |
| **API Server** | Uvicorn (ASGI) |
| **Data Handling** | pandas, numpy |

## How to Run

### Prerequisites

- Python 3.12+
- Node.js (for blockchain interactions)
- Ethereum testnet access or local blockchain

### Installation

```bash
# Clone the repository
cd FYP-Implementation

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```

### API Endpoints

- `POST /train` - Train the ML model
- `POST /predict` - Predict network traffic classification
- `POST /log-threat` - Log detected threat to blockchain

## Dataset

This project uses the **CIC-IDS2017** dataset, a widely recognized benchmark for network intrusion detection research. The dataset contains labeled network traffic including:
- Normal traffic
- Various attack types (DDoS, Port Scan, Brute Force, etc.)

> **Note**: Ensure you have the dataset file (`helo.csv` or CIC-IDS2017) in the project directory before training the model.

## Note

This project is developed as part of a Final Year Project (FYP) for academic purposes. The blockchain component uses Ethereum-compatible smart contracts for decentralized threat logging. For production deployment, ensure proper security configurations and consider using a production-grade ASGI server.
