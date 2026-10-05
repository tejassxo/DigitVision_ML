"""
DIGITVISION AI — Error Intelligence & High-Confidence Failure Analysis
======================================================================
Identifies, dissects, and categorizes failure modes. Isolates high-confidence
failures (silent errors where model confidence >= 0.80 but prediction is wrong)
and computes pairwise confusion rankings.
"""

import os
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
from src.intelligence.confidence import compute_shannon_entropy


def analyze_top_confusions(confusion_matrix_arr: np.ndarray, top_n: int = 6) -> List[Dict[str, Any]]:
    """
    Extracts the most frequent off-diagonal misclassification pairs from confusion matrix.
    """
    cm = confusion_matrix_arr.copy()
    np.fill_diagonal(cm, 0) # Zero out correct classifications

    pairs = []
    for true_c in range(10):
        for pred_c in range(10):
            if true_c != pred_c and cm[true_c, pred_c] > 0:
                pairs.append({
                    "true_class": true_c,
                    "predicted_class": pred_c,
                    "error_count": int(cm[true_c, pred_c])
                })

    pairs.sort(key=lambda x: x["error_count"], reverse=True)
    return pairs[:top_n]


def mine_high_confidence_failures(
    test_images: np.ndarray,
    test_labels: np.ndarray,
    predictions: np.ndarray,
    probabilities: np.ndarray,
    confidence_threshold: float = 0.80,
    max_saved: int = 15,
    output_dir: str = "experiments/failures"
) -> List[Dict[str, Any]]:
    """
    Mines test instances where prediction is incorrect despite high model confidence.
    Saves visual artifacts and diagnostics.
    """
    os.makedirs(output_dir, exist_ok=True)
    failures = []

    confs = np.max(probabilities, axis=1)
    wrong_indices = np.where((predictions != test_labels) & (confs >= confidence_threshold))[0]

    for rank, idx in enumerate(wrong_indices[:max_saved]):
        true_digit = int(test_labels[idx])
        pred_digit = int(predictions[idx])
        conf_val = float(confs[idx])
        probs = probabilities[idx]

        sorted_indices = np.argsort(probs)[::-1]
        runner_up_digit = int(sorted_indices[1])
        runner_up_prob = float(probs[runner_up_digit])
        entropy_bits, _ = compute_shannon_entropy(probs)

        # Save digit image
        img_raw = test_images[idx]
        img_u8 = (np.clip(img_raw, 0.0, 1.0) * 255.0).astype(np.uint8)
        img_upscaled = cv2.resize(img_u8, (140, 140), interpolation=cv2.INTER_NEAREST)

        filename = f"failure_true{true_digit}_pred{pred_digit}_idx{idx}.png"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, img_upscaled)

        failures.append({
            "sample_index": int(idx),
            "true_digit": true_digit,
            "predicted_digit": pred_digit,
            "confidence": round(conf_val, 4),
            "runner_up_digit": runner_up_digit,
            "runner_up_prob": round(runner_up_prob, 4),
            "margin": round(conf_val - runner_up_prob, 4),
            "entropy_bits": round(entropy_bits, 4),
            "artifact_path": filepath
        })

    return failures
