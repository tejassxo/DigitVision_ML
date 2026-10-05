"""
DIGITVISION AI — Production FastAPI Telemetry & Inference Server
================================================================
Serves real-time inference, Digit Forensics diagnostics, Explainable AI
overlays (Grad-CAM and Saliency), model comparisons, and interactive dashboards.
"""

import os
import sys
import json
import numpy as np
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.models.deep import DeepModelWrapper
from src.models.classical import ClassicalModelWrapper
from src.intelligence.forensics import run_full_forensics_pipeline
from src.intelligence.confidence import TemperatureScaler
import joblib

app = FastAPI(
    title="DIGITVISION AI",
    description="Explainable, Confidence-Aware Handwritten Digit Intelligence Platform",
    version="1.0.0"
)

# Enable CORS for local cross-origin development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registry of loaded models
LOADED_MODELS: Dict[str, Any] = {}
TEMPERATURE_SCALER: Optional[TemperatureScaler] = None


def get_available_models():
    """Dynamically loads or returns cached models from experiments/models/."""
    global LOADED_MODELS, TEMPERATURE_SCALER

    models_dir = os.path.abspath("experiments/models")
    if not os.path.exists(models_dir):
        return LOADED_MODELS

    # Load Temperature Scaler if available
    scaler_path = os.path.join(models_dir, "temperature_scaler.joblib")
    if TEMPERATURE_SCALER is None and os.path.exists(scaler_path):
        try:
            TEMPERATURE_SCALER = joblib.load(scaler_path)
        except Exception:
            pass

    # 1. Deep ConvNet
    convnet_path = os.path.join(models_dir, "digitvision_convnet.keras")
    if "DigitVision-DeepConvNet" not in LOADED_MODELS and os.path.exists(convnet_path):
        try:
            LOADED_MODELS["DigitVision-DeepConvNet"] = DeepModelWrapper.load(
                convnet_path, name="DigitVision-DeepConvNet", target_conv_layer="conv_cam"
            )
        except Exception as e:
            print(f"Error loading DeepConvNet: {e}")

    # 2. LeNet-5
    lenet_path = os.path.join(models_dir, "lenet5.keras")
    if "LeNet-5" not in LOADED_MODELS and os.path.exists(lenet_path):
        try:
            LOADED_MODELS["LeNet-5"] = DeepModelWrapper.load(
                lenet_path, name="LeNet-5", target_conv_layer="conv_cam"
            )
        except Exception as e:
            print(f"Error loading LeNet-5: {e}")

    # 3. Logistic Regression
    lr_path = os.path.join(models_dir, "logistic_regression.joblib")
    if "Logistic-Regression" not in LOADED_MODELS and os.path.exists(lr_path):
        try:
            LOADED_MODELS["Logistic-Regression"] = ClassicalModelWrapper.load(
                lr_path, name="Logistic-Regression"
            )
        except Exception as e:
            print(f"Error loading Logistic Regression: {e}")

    # 4. Random Forest
    rf_path = os.path.join(models_dir, "random_forest.joblib")
    if "Random-Forest" not in LOADED_MODELS and os.path.exists(rf_path):
        try:
            LOADED_MODELS["Random-Forest"] = ClassicalModelWrapper.load(
                rf_path, name="Random-Forest"
            )
        except Exception as e:
            print(f"Error loading Random Forest: {e}")

    # 5. SVM RBF
    svm_path = os.path.join(models_dir, "svm_rbf.joblib")
    if "SVM-RBF" not in LOADED_MODELS and os.path.exists(svm_path):
        try:
            LOADED_MODELS["SVM-RBF"] = ClassicalModelWrapper.load(
                svm_path, name="SVM-RBF"
            )
        except Exception as e:
            print(f"Error loading SVM-RBF: {e}")

    return LOADED_MODELS


class PredictionRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image or Data URL")
    model_id: str = Field("DigitVision-DeepConvNet", description="Selected model architecture identifier")
    generate_xai: bool = Field(True, description="Whether to compute Grad-CAM and Saliency maps")


@app.get("/api/health")
def health_check():
    models = get_available_models()
    return {
        "status": "healthy",
        "service": "DIGITVISION AI — Platform API",
        "loaded_models": list(models.keys()),
        "temperature_calibrated": TEMPERATURE_SCALER is not None
    }


@app.get("/api/models")
def list_models():
    models = get_available_models()
    model_catalog = [
        {
            "id": "DigitVision-DeepConvNet",
            "name": "DigitVision DeepConvNet",
            "type": "Deep Learning (CNN + BatchNorm + Dropout)",
            "supports_xai": True,
            "is_default": True,
            "description": "State-of-the-art multi-stage convolutional network with explicit Grad-CAM layer."
        },
        {
            "id": "LeNet-5",
            "name": "Classic LeNet-5",
            "type": "Deep Learning (Yann LeCun 1998)",
            "supports_xai": True,
            "is_default": False,
            "description": "Historical convolutional neural network baseline."
        },
        {
            "id": "SVM-RBF",
            "name": "Support Vector Machine (RBF)",
            "type": "Classical ML",
            "supports_xai": False,
            "is_default": False,
            "description": "Radial basis function kernel with maximum-margin decision boundaries."
        },
        {
            "id": "Random-Forest",
            "name": "Random Forest Ensemble",
            "type": "Classical ML",
            "supports_xai": False,
            "is_default": False,
            "description": "100-tree bagging ensemble with non-linear feature partitioning."
        },
        {
            "id": "Logistic-Regression",
            "name": "Multinomial Logistic Regression",
            "type": "Classical ML",
            "supports_xai": False,
            "is_default": False,
            "description": "Linear classifier baseline with L2 penalty."
        }
    ]
    return {
        "models": model_catalog,
        "active_models": list(models.keys())
    }


@app.post("/api/predict")
def predict_digit(req: PredictionRequest):
    models = get_available_models()

    if not models:
        raise HTTPException(
            status_code=503,
            detail="No models are currently trained or loaded. Run experiments/run_experiments.py first."
        )

    model_wrapper = models.get(req.model_id)
    if model_wrapper is None:
        # Fallback to first available model
        model_wrapper = next(iter(models.values()))

    scaler_to_use = TEMPERATURE_SCALER if model_wrapper.is_deep else None

    try:
        telemetry = run_full_forensics_pipeline(
            raw_image_input=req.image,
            model_wrapper=model_wrapper,
            scaler=scaler_to_use,
            generate_xai=req.generate_xai
        )
        return telemetry
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {str(e)}")


@app.get("/api/experiments")
def get_experiment_results():
    results_path = os.path.abspath("experiments/metrics/experiment_results.json")
    if not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Experiment results not found. Pipeline has not completed.")
    with open(results_path, "r") as f:
        data = json.load(f)
    return data


# Mount static web UI, figures, and presentation
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

figures_dir = os.path.abspath("experiments/figures")
if os.path.exists(figures_dir):
    app.mount("/figures", StaticFiles(directory=figures_dir), name="figures")

failures_dir = os.path.abspath("experiments/failures")
if os.path.exists(failures_dir):
    app.mount("/failures", StaticFiles(directory=failures_dir), name="failures")

pres_dir = os.path.abspath("src/presentation")
if os.path.exists(pres_dir):
    app.mount("/presentation", StaticFiles(directory=pres_dir), name="presentation")


@app.get("/")
def serve_dashboard():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"message": "DigitVision AI API active. Dashboard static files pending."})
