"""
DIGITVISION AI — Digit Forensics Telemetry Packager
===================================================
Produces a unified, high-density diagnostic telemetry payload
for every single inference query, binding preprocessing invariants,
quality indices, uncertainty calibration, and explainability attributions.
"""

import time
import base64
import cv2
import numpy as np
from typing import Dict, Any, Optional

from src.preprocessing.canonical import canonical_preprocess
from src.intelligence.quality import assess_input_quality
from src.intelligence.confidence import analyze_prediction_confidence, TemperatureScaler
from src.xai.gradcam import generate_gradcam_heatmap, render_gradcam_overlay
from src.xai.saliency import compute_pixel_saliency, render_saliency_overlay


def encode_grayscale_as_base64(img_28x28: np.ndarray, upscale: int = 6) -> str:
    """Encodes normalized 28x28 grayscale image as base64 PNG data URL."""
    u8 = (np.clip(img_28x28, 0.0, 1.0) * 255.0).astype(np.uint8)
    if upscale > 1:
        u8 = cv2.resize(u8, (28 * upscale, 28 * upscale), interpolation=cv2.INTER_NEAREST)
    success, encoded = cv2.imencode('.png', u8)
    if not success:
        return ""
    b64 = base64.b64encode(encoded).decode('utf-8')
    return f"data:image/png;base64,{b64}"


def run_full_forensics_pipeline(
    raw_image_input: Any,
    model_wrapper: Any,
    scaler: Optional[TemperatureScaler] = None,
    generate_xai: bool = True
) -> Dict[str, Any]:
    """
    Executes the end-to-end DigitVision Forensics telemetry pipeline:
    1. Canonical invariant preprocessing
    2. Input quality grading
    3. Model forward pass with latency timing
    4. Uncertainty calibration & Top-K ranking
    5. Grad-CAM & Saliency generation
    6. Packaging into a high-density diagnostic dictionary.
    """
    t0 = time.perf_counter()

    # 1. Canonical preprocessing
    canonical_img, prep_meta = canonical_preprocess(raw_image_input)
    t_prep = time.perf_counter()

    # 2. Quality assessment
    quality_report = assess_input_quality(canonical_img, prep_meta)

    # 3. Model inference
    model_name = getattr(model_wrapper, "name", "DigitVision-Model")
    is_deep_model = getattr(model_wrapper, "is_deep", False)

    t_infer_start = time.perf_counter()
    if quality_report["is_valid"]:
        raw_probs = model_wrapper.predict_proba(canonical_img)
    else:
        # Uniform or zero fallback for empty/invalid drawings
        raw_probs = np.full((10,), 0.1, dtype=np.float64)
    t_infer_end = time.perf_counter()

    # 4. Uncertainty & confidence analysis
    confidence_report = analyze_prediction_confidence(raw_probs, scaler=scaler, top_k=5)

    # 5. Explainable AI
    gradcam_url = None
    saliency_url = None
    if generate_xai and is_deep_model and quality_report["is_valid"]:
        try:
            keras_model = getattr(model_wrapper, "raw_model", None)
            if keras_model is not None:
                tensor_in = canonical_img.reshape(1, 28, 28, 1)
                predicted_class = confidence_report["predicted_digit"]

                heatmap, _ = generate_gradcam_heatmap(keras_model, tensor_in, target_class=predicted_class)
                gradcam_url = render_gradcam_overlay(canonical_img, heatmap, alpha=0.55)

                saliency_map, _ = compute_pixel_saliency(keras_model, tensor_in, target_class=predicted_class)
                saliency_url = render_saliency_overlay(canonical_img, saliency_map, alpha=0.60)
        except Exception as e:
            # Fallback gracefully if XAI encounters layer mismatch
            pass

    t_total = time.perf_counter()

    # Canonical preview image URL
    canonical_url = encode_grayscale_as_base64(canonical_img, upscale=6)

    # Final decision routing
    if not quality_report["is_valid"]:
        final_decision = "REJECTED_INPUT_QUALITY"
        decision_rationale = "; ".join(quality_report["reasons"])
    elif confidence_report["confidence_band"] == "HIGH":
        final_decision = "ACCEPTED_HIGH_CONFIDENCE"
        decision_rationale = f"Digit {confidence_report['predicted_digit']} recognized with {confidence_report['confidence_percentage']}% confidence (margin: {confidence_report['margin']:.2f})."
    elif confidence_report["confidence_band"] == "MODERATE":
        final_decision = "ACCEPTED_MODERATE_CONFIDENCE"
        decision_rationale = f"Digit {confidence_report['predicted_digit']} predicted with moderate confidence. Secondary runner-up is {confidence_report['runner_up_digit']} ({confidence_report['runner_up_prob']*100:.1f}%)."
    else:
        final_decision = "FLAGGED_AMBIGUOUS_DISTRIBUTION"
        decision_rationale = f"Prediction uncertainty is high (entropy: {confidence_report['entropy_bits']:.2f} bits, margin: {confidence_report['margin']:.2f}). Possible out-of-distribution stroke."

    return {
        "telemetry_version": "1.0.0",
        "timestamp_unix": time.time(),
        "model_id": model_name,
        "is_deep_architecture": is_deep_model,
        "execution_latency_ms": {
            "preprocessing": round((t_prep - t0) * 1000.0, 3),
            "inference": round((t_infer_end - t_infer_start) * 1000.0, 3),
            "total_roundtrip": round((t_total - t0) * 1000.0, 3)
        },
        "decision": {
            "status": final_decision,
            "rationale": decision_rationale,
            "theme_color": confidence_report["theme_color"] if quality_report["is_valid"] else "#FF3333"
        },
        "prediction": confidence_report,
        "quality_audit": quality_report,
        "preprocessing_metadata": {
            "is_empty": prep_meta.get("is_empty", False),
            "dx_shift": round(prep_meta.get("dx", 0.0), 2),
            "dy_shift": round(prep_meta.get("dy", 0.0), 2),
            "active_pixel_ratio": round(prep_meta.get("active_pixel_ratio", 0.0), 4)
        },
        "visual_artifacts": {
            "canonical_preview": canonical_url,
            "gradcam_overlay": gradcam_url,
            "saliency_overlay": saliency_url
        }
    }
