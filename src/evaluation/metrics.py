"""
DIGITVISION AI — Quantitative Evaluation & Calibration Metrics
==============================================================
Calculates multi-class classification metrics, Expected Calibration Error (ECE),
reliability diagram bins, latency profiles, and macro/micro metrics.
"""

import time
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)


def compute_expected_calibration_error(
    confidences: np.ndarray,
    predictions: np.ndarray,
    labels: np.ndarray,
    n_bins: int = 15
) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Computes Expected Calibration Error (ECE) and reliability diagram bins:
    ECE = sum_m (|B_m| / N) * |acc(B_m) - conf(B_m)|.

    Args:
        confidences: 1D array of Top-1 predicted confidences in [0, 1].
        predictions: 1D array of Top-1 predicted class indices.
        labels: 1D array of ground truth labels.
        n_bins: Number of confidence bins (default 15).

    Returns:
        ece: Scalar Expected Calibration Error.
        bins_data: List of bin statistics (bin_range, accuracy, avg_confidence, count).
    """
    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    accuracies = (predictions == labels).astype(np.float64)
    total_samples = len(labels)

    ece = 0.0
    bins_data: List[Dict[str, Any]] = []

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]

        if i == n_bins - 1:
            in_bin = (confidences >= bin_lower) & (confidences <= bin_upper)
        else:
            in_bin = (confidences >= bin_lower) & (confidences < bin_upper)

        bin_count = int(np.sum(in_bin))
        if bin_count > 0:
            bin_acc = float(np.mean(accuracies[in_bin]))
            bin_conf = float(np.mean(confidences[in_bin]))
            bin_weight = bin_count / total_samples
            ece += bin_weight * abs(bin_acc - bin_conf)
        else:
            bin_acc = 0.0
            bin_conf = float((bin_lower + bin_upper) / 2.0)

        bins_data.append({
            "bin_index": i,
            "bin_lower": round(float(bin_lower), 3),
            "bin_upper": round(float(bin_upper), 3),
            "sample_count": bin_count,
            "accuracy": round(bin_acc, 4),
            "confidence": round(bin_conf, 4)
        })

    return float(ece), bins_data


def benchmark_inference_latency(
    model_wrapper: Any,
    sample_img: np.ndarray,
    warmup_runs: int = 50,
    test_runs: int = 500
) -> Dict[str, float]:
    """
    Rigorously benchmarks per-sample inference latency across multiple runs.
    """
    # Warmup
    for _ in range(warmup_runs):
        _ = model_wrapper.predict_proba(sample_img)

    durations = []
    for _ in range(test_runs):
        t0 = time.perf_counter()
        _ = model_wrapper.predict_proba(sample_img)
        t1 = time.perf_counter()
        durations.append((t1 - t0) * 1000.0) # in ms

    durations_arr = np.array(durations)
    return {
        "mean_latency_ms": round(float(np.mean(durations_arr)), 3),
        "std_latency_ms": round(float(np.std(durations_arr)), 3),
        "median_latency_ms": round(float(np.median(durations_arr)), 3),
        "p95_latency_ms": round(float(np.percentile(durations_arr, 95)), 3),
        "p99_latency_ms": round(float(np.percentile(durations_arr, 99)), 3),
        "throughput_samples_per_sec": round(1000.0 / max(0.001, float(np.mean(durations_arr))), 1)
    }


def evaluate_model_full(
    model_wrapper: Any,
    test_images: np.ndarray,
    test_labels: np.ndarray,
    batch_size: int = 256
) -> Dict[str, Any]:
    """
    Performs comprehensive evaluation of a model on the isolated test set.
    """
    n_samples = len(test_labels)

    # Compute probabilities
    if hasattr(model_wrapper, "predict_batch_proba"):
        probs = model_wrapper.predict_batch_proba(test_images, batch_size=batch_size)
    else:
        # Classical model batch iteration
        flat_imgs = test_images.reshape(n_samples, -1)
        probs = model_wrapper.model.predict_proba(flat_imgs)

    preds = np.argmax(probs, axis=1)
    confs = np.max(probs, axis=1)

    # Classification metrics
    acc = float(accuracy_score(test_labels, preds))
    prec, rec, f1, sup = precision_recall_fscore_support(test_labels, preds, average=None)
    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(test_labels, preds, average='macro')
    prec_weight, rec_weight, f1_weight, _ = precision_recall_fscore_support(test_labels, preds, average='weighted')

    # Confusion matrix
    cm = confusion_matrix(test_labels, preds, labels=list(range(10)))

    # Calibration ECE
    ece, ece_bins = compute_expected_calibration_error(confs, preds, test_labels, n_bins=15)

    # Latency benchmark
    latency_profile = benchmark_inference_latency(model_wrapper, test_images[0], warmup_runs=20, test_runs=200)

    per_class_metrics = {}
    for digit in range(10):
        per_class_metrics[str(digit)] = {
            "precision": round(float(prec[digit]), 4),
            "recall": round(float(rec[digit]), 4),
            "f1_score": round(float(f1[digit]), 4),
            "support": int(sup[digit])
        }

    return {
        "model_name": model_wrapper.name,
        "is_deep": model_wrapper.is_deep,
        "test_sample_count": n_samples,
        "accuracy": round(acc, 4),
        "accuracy_pct": round(acc * 100.0, 2),
        "macro_precision": round(float(prec_macro), 4),
        "macro_recall": round(float(rec_macro), 4),
        "macro_f1": round(float(f1_macro), 4),
        "weighted_f1": round(float(f1_weight), 4),
        "expected_calibration_error": round(ece, 4),
        "calibration_bins": ece_bins,
        "confusion_matrix": cm.tolist(),
        "per_class": per_class_metrics,
        "latency": latency_profile,
        "predictions": preds,
        "probabilities": probs,
        "confidences": confs
    }
