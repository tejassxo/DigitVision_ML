"""
DIGITVISION AI — Confidence-Aware Prediction & Uncertainty Calibration
======================================================================
Implements rigorous probability calibration via temperature scaling,
Shannon entropy calculation, top-K margin analysis, and multi-tier
decision boundaries for reliable rejection and verification.
"""

import numpy as np
from scipy.optimize import minimize
from typing import Dict, Any, List, Tuple, Optional


class TemperatureScaler:
    """
    Post-hoc probability calibrator using temperature scaling (Guo et al., 2017).
    Optimizes a single scalar T > 0 on validation logits using cross-entropy loss.
    """
    def __init__(self, temperature: float = 1.0):
        self.temperature = float(temperature)

    def fit(self, logits: np.ndarray, labels: np.ndarray) -> float:
        """
        Fits temperature T on validation logits and true integer labels.
        """
        labels = np.asarray(labels, dtype=np.int64)
        n_samples = len(labels)

        def nll_objective(T_val):
            T = T_val[0]
            if T <= 0:
                return 1e9
            scaled_logits = logits / T
            # Numerically stable log-softmax
            max_l = np.max(scaled_logits, axis=1, keepdims=True)
            log_sum_exp = max_l + np.log(np.sum(np.exp(scaled_logits - max_l), axis=1, keepdims=True))
            log_probs = scaled_logits - log_sum_exp
            nll = -np.sum(log_probs[np.arange(n_samples), labels]) / n_samples
            return nll

        res = minimize(nll_objective, x0=[self.temperature], bounds=[(0.05, 10.0)], method='L-BFGS-B')
        if res.success:
            self.temperature = float(res.x[0])
        return self.temperature

    def calibrate_logits(self, logits: np.ndarray) -> np.ndarray:
        """Applies temperature scaling to logits and returns calibrated probabilities."""
        scaled = logits / self.temperature
        exp_scaled = np.exp(scaled - np.max(scaled, axis=-1, keepdims=True))
        return exp_scaled / np.sum(exp_scaled, axis=-1, keepdims=True)

    def calibrate_probabilities(self, probs: np.ndarray) -> np.ndarray:
        """
        Converts probability distribution to pseudo-logits, applies T, and returns calibrated probs.
        """
        eps = 1e-12
        probs = np.clip(probs, eps, 1.0 - eps)
        pseudo_logits = np.log(probs)
        return self.calibrate_logits(pseudo_logits)


def compute_shannon_entropy(probs: np.ndarray) -> Tuple[float, float]:
    """
    Computes Shannon entropy H(p) in bits and normalized entropy [0.0, 1.0].
    H(p) = - sum_i p_i * log2(p_i).
    Max entropy for 10 classes is log2(10) ~ 3.3219 bits.
    """
    eps = 1e-12
    clipped = np.clip(probs, eps, 1.0)
    entropy_bits = -float(np.sum(clipped * np.log2(clipped)))
    max_entropy = np.log2(len(probs))
    normalized_entropy = float(entropy_bits / max_entropy)
    return entropy_bits, normalized_entropy


def analyze_prediction_confidence(
    probs: np.ndarray,
    scaler: Optional[TemperatureScaler] = None,
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Computes full confidence and uncertainty telemetry for a 10-class probability distribution.

    Args:
        probs: 1D array of length 10 summing to 1.0.
        scaler: Optional fitted TemperatureScaler instance.
        top_k: Number of ranked predictions to return (default 5).

    Returns:
        Structured confidence diagnostics dictionary.
    """
    probs = np.asarray(probs, dtype=np.float64).flatten()
    if np.sum(probs) > 0:
        probs = probs / np.sum(probs)

    # Calibrated probabilities
    if scaler is not None:
        calibrated_probs = scaler.calibrate_probabilities(probs)
    else:
        calibrated_probs = probs.copy()

    # Sort classes by descending probability
    sorted_indices = np.argsort(calibrated_probs)[::-1]
    top1_class = int(sorted_indices[0])
    top2_class = int(sorted_indices[1])

    top1_prob = float(calibrated_probs[top1_class])
    top2_prob = float(calibrated_probs[top2_class])

    # Margin of confidence
    margin = top1_prob - top2_prob

    # Shannon Entropy
    entropy_bits, norm_entropy = compute_shannon_entropy(calibrated_probs)

    # Decision Categorization & Color Palette assignment
    # Deep Obsidian palette standards:
    # High: #1DB954, Moderate: #FFB000, Low / Ambiguous: #FF3333
    if top1_prob >= 0.85 and margin >= 0.60 and norm_entropy <= 0.35:
        confidence_band = "HIGH"
        status_label = "VERIFIED_HIGH_CONFIDENCE"
        theme_color = "#1DB954"
    elif top1_prob >= 0.50 and margin >= 0.20 and norm_entropy <= 0.65:
        confidence_band = "MODERATE"
        status_label = "REASONABLE_CONFIDENCE"
        theme_color = "#FFB000"
    else:
        confidence_band = "LOW"
        status_label = "AMBIGUOUS_OR_OOD"
        theme_color = "#FF3333"

    # Build Top-K ranking list
    top_k_list: List[Dict[str, Any]] = []
    for rank, idx in enumerate(sorted_indices[:top_k], start=1):
        p = float(calibrated_probs[idx])
        top_k_list.append({
            "rank": rank,
            "digit": int(idx),
            "probability": round(p, 4),
            "percentage": round(p * 100.0, 2),
            "raw_probability": round(float(probs[idx]), 4)
        })

    return {
        "predicted_digit": top1_class,
        "confidence": round(top1_prob, 4),
        "confidence_percentage": round(top1_prob * 100.0, 2),
        "confidence_band": confidence_band,
        "status_label": status_label,
        "theme_color": theme_color,
        "margin": round(margin, 4),
        "runner_up_digit": top2_class,
        "runner_up_prob": round(top2_prob, 4),
        "entropy_bits": round(entropy_bits, 4),
        "normalized_entropy": round(norm_entropy, 4),
        "top_k": top_k_list,
        "all_probabilities": [round(float(p), 4) for p in calibrated_probs]
    }
