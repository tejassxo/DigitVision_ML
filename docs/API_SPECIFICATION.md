# DIGITVISION AI — REST API SPECIFICATION

> **Production Telemetry & Inference REST Interface**  
> *Base URL: `http://localhost:8000`*

---

## 1. Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status, GPU/CPU engine, and loaded models. |
| `GET` | `/api/models` | Catalog of available neural and classical models. |
| `POST` | `/api/predict` | Primary inference endpoint with Digit Forensics telemetry and XAI. |
| `GET` | `/api/experiments` | Empirical benchmark results from `experiment_results.json`. |
| `GET` | `/` | Serves interactive Deep Obsidian web dashboard. |
| `GET` | `/presentation/slides.html`| Serves standalone interactive technical presentation deck. |

---

## 2. Endpoint Details

### 2.1 `GET /api/health`
Returns runtime status and loaded model architectures.

#### Response `200 OK`:
```json
{
  "status": "healthy",
  "service": "DIGITVISION AI — Platform API",
  "loaded_models": [
    "DigitVision-DeepConvNet",
    "LeNet-5",
    "Logistic-Regression",
    "Random-Forest",
    "SVM-RBF"
  ],
  "temperature_calibrated": true
}
```

---

### 2.2 `GET /api/models`
Returns available model options with metadata and XAI support tags.

#### Response `200 OK`:
```json
{
  "models": [
    {
      "id": "DigitVision-DeepConvNet",
      "name": "DigitVision DeepConvNet",
      "type": "Deep Learning (CNN + BatchNorm + Dropout)",
      "supports_xai": true,
      "is_default": true,
      "description": "State-of-the-art multi-stage convolutional network with explicit Grad-CAM layer."
    },
    {
      "id": "LeNet-5",
      "name": "Classic LeNet-5",
      "type": "Deep Learning (Yann LeCun 1998)",
      "supports_xai": true,
      "is_default": false,
      "description": "Historical convolutional neural network baseline."
    }
  ],
  "active_models": ["DigitVision-DeepConvNet", "LeNet-5"]
}
```

---

### 2.3 `POST /api/predict`
Executes canonical preprocessing, input-quality validation, model forward pass, uncertainty calibration, and Grad-CAM/Saliency visual rendering.

#### Request Body:
```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "model_id": "DigitVision-DeepConvNet",
  "generate_xai": true
}
```

#### Response `200 OK` (Standard Acceptance):
```json
{
  "telemetry_version": "1.0.0",
  "timestamp_unix": 1728131000.123,
  "model_id": "DigitVision-DeepConvNet",
  "is_deep_architecture": true,
  "execution_latency_ms": {
    "preprocessing": 0.35,
    "inference": 1.45,
    "total_roundtrip": 1.80
  },
  "decision": {
    "status": "ACCEPTED_HIGH_CONFIDENCE",
    "rationale": "Digit 7 recognized with 99.42% confidence (margin: 0.98).",
    "theme_color": "#1DB954"
  },
  "prediction": {
    "predicted_digit": 7,
    "confidence": 0.9942,
    "confidence_percentage": 99.42,
    "confidence_band": "HIGH",
    "status_label": "VERIFIED_HIGH_CONFIDENCE",
    "theme_color": "#1DB954",
    "margin": 0.9884,
    "runner_up_digit": 1,
    "runner_up_prob": 0.0058,
    "entropy_bits": 0.052,
    "normalized_entropy": 0.015,
    "top_k": [
      {
        "rank": 1,
        "digit": 7,
        "probability": 0.9942,
        "percentage": 99.42,
        "raw_probability": 0.9951
      }
    ],
    "all_probabilities": [0.0, 0.0058, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9942, 0.0, 0.0]
  },
  "quality_audit": {
    "quality_score": 96.5,
    "quality_band": "OPTIMAL",
    "is_valid": true,
    "reasons": [],
    "stroke_pixel_count": 84,
    "bounding_box_coverage": 0.107,
    "aspect_ratio": 0.75,
    "centroid_offset": 0.42,
    "sharpness": 142.5,
    "noise_ratio": 0.0,
    "warnings": []
  },
  "preprocessing_metadata": {
    "is_empty": false,
    "dx_shift": 1.25,
    "dy_shift": -0.85,
    "active_pixel_ratio": 0.107
  },
  "visual_artifacts": {
    "canonical_preview": "data:image/png;base64,...",
    "gradcam_overlay": "data:image/png;base64,...",
    "saliency_overlay": "data:image/png;base64,..."
  }
}
```

#### Response `200 OK` (Quality Rejection):
```json
{
  "decision": {
    "status": "REJECTED_INPUT_QUALITY",
    "rationale": "Canvas is blank. No stroke detected.",
    "theme_color": "#FF3333"
  },
  "quality_audit": {
    "quality_score": 0.0,
    "quality_band": "INVALID_EMPTY",
    "is_valid": false,
    "reasons": ["Canvas is blank. No stroke detected."],
    "warnings": ["EMPTY_CANVAS"]
  }
}
```
