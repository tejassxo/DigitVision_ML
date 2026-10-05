"""
DIGITVISION AI — Unit Tests: Input-Quality & Confidence Intelligence
===================================================================
Tests quality scoring heuristics, Shannon entropy bounds, prediction margin,
and temperature scaling calibration behavior.
"""

import pytest
import numpy as np
from src.intelligence.quality import assess_input_quality
from src.intelligence.confidence import (
    compute_shannon_entropy,
    analyze_prediction_confidence,
    TemperatureScaler
)


def test_quality_on_empty_canvas():
    """Verify empty canvas is assessed as invalid with zero quality score."""
    blank = np.zeros((28, 28), dtype=np.float32)
    meta = {"is_empty": True}
    res = assess_input_quality(blank, meta)

    assert res["is_valid"] is False
    assert res["quality_score"] == 0.0
    assert "EMPTY_CANVAS" in res["warnings"]


def test_quality_on_valid_digit():
    """Verify clean stroke image yields acceptable/optimal quality score."""
    img = np.zeros((28, 28), dtype=np.float32)
    # Draw a clean stroke
    img[6:22, 12:15] = 0.95
    meta = {
        "is_empty": False,
        "centroid_final": (13.5, 13.5),
        "bbox": {"x": 12, "y": 6, "w": 3, "h": 16}
    }
    res = assess_input_quality(img, meta)

    assert res["is_valid"] is True
    assert res["quality_score"] >= 60.0
    assert res["stroke_pixel_count"] > 20


def test_shannon_entropy_bounds():
    """
    Test Shannon entropy bounds:
    - Degenerate one-hot distribution: 0.0 bits
    - Uniform 10-class distribution: log2(10) ~ 3.3219 bits
    """
    one_hot = np.zeros(10)
    one_hot[3] = 1.0
    h_min, norm_h_min = compute_shannon_entropy(one_hot)
    assert abs(h_min) < 1e-4
    assert abs(norm_h_min) < 1e-4

    uniform = np.full(10, 0.1)
    h_max, norm_h_max = compute_shannon_entropy(uniform)
    expected_h = np.log2(10)
    assert abs(h_max - expected_h) < 1e-3
    assert abs(norm_h_max - 1.0) < 1e-3


def test_confidence_telemetry_high():
    """Verify high-confidence distribution is classified correctly."""
    probs = np.zeros(10)
    probs[7] = 0.92
    probs[1] = 0.05
    probs[2] = 0.03

    diag = analyze_prediction_confidence(probs, top_k=5)
    assert diag["predicted_digit"] == 7
    assert diag["confidence"] == 0.92
    assert diag["confidence_band"] == "HIGH"
    assert diag["theme_color"] == "#1DB954"
    assert diag["margin"] == round(0.92 - 0.05, 4)
    assert len(diag["top_k"]) == 5


def test_confidence_telemetry_low():
    """Verify ambiguous distribution is categorized as LOW."""
    probs = np.full(10, 0.1)
    probs[4] = 0.22
    probs[9] = 0.20
    probs[8] = 0.15
    probs /= np.sum(probs)

    diag = analyze_prediction_confidence(probs, top_k=5)
    assert diag["confidence_band"] == "LOW"
    assert diag["theme_color"] == "#FF3333"


def test_temperature_scaler():
    """Verify temperature scaler softens probabilities when T > 1."""
    scaler = TemperatureScaler(temperature=2.0)
    probs = np.array([0.8, 0.1, 0.05, 0.05, 0, 0, 0, 0, 0, 0])
    calibrated = scaler.calibrate_probabilities(probs)

    # When T > 1, max prob should decrease towards uniformity
    assert calibrated[0] < probs[0]
    assert np.isclose(np.sum(calibrated), 1.0)
