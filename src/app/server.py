"""
DIGITVISION AI — Production FastAPI Telemetry & Inference Server
================================================================
Serves real-time inference, Digit Forensics diagnostics, Explainable AI
overlays (Grad-CAM and Saliency), model comparisons, confusion matrices,
error analytics, and modern Apple Pro / Deep Obsidian dashboards.
"""

import os
import sys
import json
import csv
import numpy as np
from typing import Dict, Any, Optional, List, Union
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
    version="1.2.0"
)

# Enable CORS for production and local environments
origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Registry of loaded models
LOADED_MODELS: Dict[str, Any] = {}
TEMPERATURE_SCALER: Optional[TemperatureScaler] = None

# Model alias normalization map
MODEL_ALIASES: Dict[str, str] = {
    "cnn_v1": "DigitVision-DeepConvNet",
    "digitvision-deepconvnet": "DigitVision-DeepConvNet",
    "digitvision_convnet": "DigitVision-DeepConvNet",
    "convnet": "DigitVision-DeepConvNet",
    "cnn": "DigitVision-DeepConvNet",
    "lenet5": "LeNet-5",
    "lenet-5": "LeNet-5",
    "lenet": "LeNet-5",
    "mlp_baseline": "MLP-Deep",
    "mlp-deep": "MLP-Deep",
    "mlp": "MLP-Deep",
    "svm_baseline": "SVM-RBF",
    "svm-rbf": "SVM-RBF",
    "svm": "SVM-RBF",
    "logreg_baseline": "Logistic-Regression",
    "logistic-regression": "Logistic-Regression",
    "logreg": "Logistic-Regression",
    "random_forest": "Random-Forest",
    "random-forest": "Random-Forest",
    "rf": "Random-Forest"
}


def get_available_models() -> Dict[str, Any]:
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

    # 3. MLP Deep
    mlp_path = os.path.join(models_dir, "mlp.keras")
    if "MLP-Deep" not in LOADED_MODELS and os.path.exists(mlp_path):
        try:
            LOADED_MODELS["MLP-Deep"] = DeepModelWrapper.load(
                mlp_path, name="MLP-Deep", target_conv_layer="dense_1"
            )
        except Exception as e:
            print(f"Error loading MLP-Deep: {e}")

    # 4. Logistic Regression
    lr_path = os.path.join(models_dir, "logistic_regression.joblib")
    if "Logistic-Regression" not in LOADED_MODELS and os.path.exists(lr_path):
        try:
            LOADED_MODELS["Logistic-Regression"] = ClassicalModelWrapper.load(
                lr_path, name="Logistic-Regression"
            )
        except Exception as e:
            print(f"Error loading Logistic Regression: {e}")

    # 5. Random Forest
    rf_path = os.path.join(models_dir, "random_forest.joblib")
    if "Random-Forest" not in LOADED_MODELS and os.path.exists(rf_path):
        try:
            LOADED_MODELS["Random-Forest"] = ClassicalModelWrapper.load(
                rf_path, name="Random-Forest"
            )
        except Exception as e:
            print(f"Error loading Random Forest: {e}")

    # 6. SVM RBF
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
    image: Optional[str] = Field(None, description="Base64 encoded image or Data URL")
    image_base64: Optional[str] = Field(None, description="Alternative Base64 field name")
    model_id: Optional[str] = Field(None, description="Selected model architecture identifier")
    model_name: Optional[str] = Field(None, description="Alternative model name selector")
    generate_xai: bool = Field(True, description="Whether to compute Grad-CAM and Saliency maps")


@app.get("/api/health")
def health_check():
    models = get_available_models()
    return {
        "status": "healthy",
        "system": "DIGITVISION AI — Platform API",
        "device": "CPU",
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
            "id": "MLP-Deep",
            "name": "Deep MLP",
            "type": "Neural Network (3-Layer FC)",
            "supports_xai": False,
            "is_default": False,
            "description": "Multi-layer perceptron with non-linear activations."
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
    img_data = req.image_base64 or req.image
    if not img_data:
        raise HTTPException(status_code=400, detail="Missing required image data (base64 string).")

    raw_model_key = req.model_name or req.model_id or "DigitVision-DeepConvNet"
    normalized_key = MODEL_ALIASES.get(raw_model_key.lower(), raw_model_key)

    models = get_available_models()
    if not models:
        raise HTTPException(
            status_code=503,
            detail="No models are currently loaded in the engine."
        )

    model_wrapper = models.get(normalized_key)
    if model_wrapper is None:
        # Fallback to DeepConvNet or first available
        model_wrapper = models.get("DigitVision-DeepConvNet", next(iter(models.values())))

    scaler_to_use = TEMPERATURE_SCALER if getattr(model_wrapper, "is_deep", False) else None

    try:
        telemetry = run_full_forensics_pipeline(
            raw_image_input=img_data,
            model_wrapper=model_wrapper,
            scaler=scaler_to_use,
            generate_xai=req.generate_xai
        )

        # Standardize flat attributes for backwards/forward UI contract compatibility
        pred_obj = telemetry.get("prediction", {})
        decision_obj = telemetry.get("decision", {})
        visual_obj = telemetry.get("visual_artifacts", {})
        latency_obj = telemetry.get("execution_latency_ms", {})
        quality_obj = telemetry.get("quality_audit", {})
        prep_meta = telemetry.get("preprocessing_metadata", {})

        top_k_candidates = pred_obj.get("top_k_candidates", [])

        # Build clean base64 image strings without prefix if requested
        canonical_b64 = visual_obj.get("canonical_preview", "")
        if canonical_b64 and "," in canonical_b64:
            canonical_b64_raw = canonical_b64.split(",", 1)[1]
        else:
            canonical_b64_raw = canonical_b64

        gradcam_b64 = visual_obj.get("gradcam_overlay", "")
        if gradcam_b64 and "," in gradcam_b64:
            gradcam_b64_raw = gradcam_b64.split(",", 1)[1]
        else:
            gradcam_b64_raw = gradcam_b64

        saliency_b64 = visual_obj.get("saliency_overlay", "")
        if saliency_b64 and "," in saliency_b64:
            saliency_b64_raw = saliency_b64.split(",", 1)[1]
        else:
            saliency_b64_raw = saliency_b64

        status_str = decision_obj.get("status", "ACCEPTED_HIGH_CONFIDENCE")
        if "HIGH" in status_str:
            clean_status = "HIGH_CONFIDENCE"
        elif "MODERATE" in status_str:
            clean_status = "MODERATE_CONFIDENCE"
        elif "REJECTED" in status_str:
            clean_status = "REJECTED_INPUT"
        else:
            clean_status = "LOW_CONFIDENCE"

        # Merge flat top-level contracts with full diagnostic tree
        telemetry.update({
            "prediction": pred_obj.get("predicted_digit", 0),
            "confidence": pred_obj.get("confidence", 0.0),
            "status": clean_status,
            "top_3": top_k_candidates[:3],
            "top_k": top_k_candidates,
            "entropy": pred_obj.get("entropy_bits", 0.0),
            "margin": pred_obj.get("margin", 0.0),
            "input_quality": quality_obj.get("grade", "GOOD"),
            "inference_latency_ms": latency_obj.get("total_roundtrip", 1.0),
            "canonical_28x28_base64": canonical_b64_raw,
            "gradcam_base64": gradcam_b64_raw,
            "saliency_base64": saliency_b64_raw,
            "processed_tensor_28x28_base64": canonical_b64_raw,
            "forensics_metadata": {
                "foreground_occupancy": prep_meta.get("active_pixel_ratio", 0.0),
                "stroke_bounding_box": [0, 0, 20, 20],
                "aspect_ratio": quality_obj.get("metrics", {}).get("aspect_ratio", 1.0),
                "center_of_mass": [prep_meta.get("dx_shift", 0.0), prep_meta.get("dy_shift", 0.0)],
                "dx": prep_meta.get("dx_shift", 0.0),
                "dy": prep_meta.get("dy_shift", 0.0)
            }
        })

        return telemetry
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {str(e)}")


@app.get("/api/experiments")
def get_experiment_results():
    """Returns structured benchmark metrics from JSON and CSV artifacts."""
    results_path = os.path.abspath("experiments/metrics/experiment_results.json")
    if os.path.exists(results_path):
        with open(results_path, "r") as f:
            data = json.load(f)
    else:
        data = {"models": {}}

    # Also build clean tabular experiments list
    experiments = []
    csv_path = os.path.abspath("artifacts/experiment_results.csv")
    if os.path.exists(csv_path):
        with open(csv_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    experiments.append({
                        "model_name": row.get("model", ""),
                        "architecture": row.get("architecture", ""),
                        "parameter_count": int(row.get("parameter_count", 0)),
                        "inference_latency_ms": float(row.get("inference_latency", 0.0)),
                        "val_loss": float(row.get("validation_loss", 0.0)) if row.get("validation_loss") not in ["N/A", ""] else "N/A",
                        "test_accuracy": float(row.get("test_accuracy", 0.0)),
                        "macro_f1": float(row.get("macro_f1", 0.0)),
                        "weighted_f1": float(row.get("weighted_f1", 0.0)),
                        "precision": float(row.get("precision", 0.0)),
                        "recall": float(row.get("recall", 0.0))
                    })
                except Exception:
                    pass

    data["experiments"] = experiments
    return data


@app.get("/api/confusion")
def get_confusion_matrix(model: str = "DigitVision-DeepConvNet"):
    """Returns raw and normalized confusion matrix for the specified model."""
    results_path = os.path.abspath("experiments/metrics/experiment_results.json")
    if not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Metrics artifact not found.")

    with open(results_path, "r") as f:
        data = json.load(f)

    models_data = data.get("models", {})
    target_model = models_data.get(model) or models_data.get("DigitVision-DeepConvNet") or next(iter(models_data.values()), None)

    if not target_model or "confusion_matrix" not in target_model:
        raise HTTPException(status_code=404, detail=f"Confusion matrix for {model} not found.")

    raw_matrix = target_model["confusion_matrix"]
    norm_matrix = []
    for row in raw_matrix:
        row_sum = sum(row)
        if row_sum > 0:
            norm_matrix.append([round(val / row_sum, 4) for val in row])
        else:
            norm_matrix.append([0.0] * len(row))

    return {
        "model_name": target_model.get("model_name", model),
        "labels": list(range(len(raw_matrix))),
        "confusion_matrix": raw_matrix,
        "normalized_matrix": norm_matrix
    }


@app.get("/api/errors")
def get_error_samples(model: str = "DigitVision-DeepConvNet"):
    """Returns representative high-confidence failure samples."""
    results_path = os.path.abspath("experiments/metrics/experiment_results.json")
    if not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Metrics artifact not found.")

    with open(results_path, "r") as f:
        data = json.load(f)

    models_data = data.get("models", {})
    target_model = models_data.get(model) or models_data.get("DigitVision-DeepConvNet") or next(iter(models_data.values()), None)

    if not target_model:
        raise HTTPException(status_code=404, detail=f"Model data for {model} not found.")

    failures = target_model.get("high_confidence_failures", [])
    formatted_errors = []
    for f in failures:
        artifact = f.get("artifact_path", "")
        # Standardize web URL path
        filename = os.path.basename(artifact)
        image_url = f"/failures/{filename}" if filename else ""

        formatted_errors.append({
            "sample_index": f.get("sample_index"),
            "true_digit": f.get("true_digit"),
            "predicted_digit": f.get("predicted_digit"),
            "confidence": f.get("confidence"),
            "runner_up_digit": f.get("runner_up_digit"),
            "runner_up_prob": f.get("runner_up_prob"),
            "margin": f.get("margin"),
            "entropy_bits": f.get("entropy_bits"),
            "image_url": image_url
        })

    return {
        "model_name": target_model.get("model_name", model),
        "total_failures": len(formatted_errors),
        "errors": formatted_errors
    }


# Static file mounts
public_dir = os.path.abspath("public")
if os.path.exists(public_dir):
    css_dir = os.path.join(public_dir, "css")
    js_dir = os.path.join(public_dir, "js")
    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="public-css")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="public-js")

static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

figures_dir = os.path.abspath("experiments/figures")
if os.path.exists(figures_dir):
    app.mount("/figures", StaticFiles(directory=figures_dir), name="figures")
    app.mount("/experiments/figures", StaticFiles(directory=figures_dir), name="experiments-figures")

failures_dir = os.path.abspath("experiments/failures")
if os.path.exists(failures_dir):
    app.mount("/failures", StaticFiles(directory=failures_dir), name="failures")

pres_dir = os.path.abspath("src/presentation")
if os.path.exists(pres_dir):
    app.mount("/presentation", StaticFiles(directory=pres_dir), name="presentation")

artifacts_dir = os.path.abspath("artifacts")
if os.path.exists(artifacts_dir):
    app.mount("/artifacts", StaticFiles(directory=artifacts_dir), name="artifacts")


@app.get("/")
def serve_dashboard():
    # Prefer public/index.html, fallback to static/index.html
    pub_index = os.path.join(public_dir, "index.html")
    if os.path.exists(pub_index):
        return FileResponse(pub_index)
    static_index = os.path.join(static_dir, "index.html")
    if os.path.exists(static_index):
        return FileResponse(static_index)
    return JSONResponse({"message": "DigitVision AI API active. Dashboard files pending."})
