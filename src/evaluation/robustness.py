"""
DIGITVISION AI — Real-World Distribution Shift & Perturbation Benchmark
=======================================================================
Evaluates model robustness under 6 realistic distribution shift corruptions:
1. Gaussian Additive Noise
2. Extreme Rotation (+/- 15 deg to +/- 45 deg)
3. Affine Shear Distortion
4. Stroke Thickness Dilation / Morphological Erosion
5. Centroid Misalignment / Translation
6. Low Contrast Attenuation (Faint Ink)
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Callable
from sklearn.metrics import accuracy_score


def apply_gaussian_noise(img: np.ndarray, severity: int) -> np.ndarray:
    """Adds zero-mean Gaussian noise scaled by severity level (1-5)."""
    sigma = [0.06, 0.12, 0.20, 0.28, 0.38][severity - 1]
    noise = np.random.normal(0, sigma, img.shape)
    return np.clip(img + noise, 0.0, 1.0).astype(np.float32)


def apply_rotation(img: np.ndarray, severity: int) -> np.ndarray:
    """Rotates image by increasing angles (+/- 10 deg to +/- 45 deg)."""
    angles = [12.0, 20.0, 30.0, 40.0, 50.0]
    angle = angles[severity - 1]
    # Alternating positive / negative
    if np.random.rand() > 0.5:
        angle = -angle
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return rotated.astype(np.float32)


def apply_shear(img: np.ndarray, severity: int) -> np.ndarray:
    """Applies affine shear distortion."""
    shear_factors = [0.10, 0.20, 0.30, 0.40, 0.50]
    shear = shear_factors[severity - 1]
    h, w = img.shape[:2]
    M = np.float32([[1, shear, -shear * (h / 2.0)], [0, 1, 0]])
    sheared = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return sheared.astype(np.float32)


def apply_stroke_morphology(img: np.ndarray, severity: int) -> np.ndarray:
    """Dilation / Erosion representing varying pen/marker thickness."""
    u8 = (img * 255.0).astype(np.uint8)
    kernel_sizes = [2, 2, 3, 3, 4]
    k_size = kernel_sizes[severity - 1]
    kernel = np.ones((k_size, k_size), np.uint8)
    if severity % 2 == 1:
        # Dilation (thick marker)
        morph = cv2.dilate(u8, kernel, iterations=1)
    else:
        # Erosion (faint ballpoint pen)
        morph = cv2.erode(u8, kernel, iterations=1)
    return (morph / 255.0).astype(np.float32)


def apply_translation(img: np.ndarray, severity: int) -> np.ndarray:
    """Translates digit off-center."""
    shifts = [2, 3, 4, 5, 6]
    s = shifts[severity - 1]
    dx = s if np.random.rand() > 0.5 else -s
    dy = s if np.random.rand() > 0.5 else -s
    h, w = img.shape[:2]
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    shifted = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return shifted.astype(np.float32)


def apply_contrast_attenuation(img: np.ndarray, severity: int) -> np.ndarray:
    """Simulates faint ink or poor lighting scan."""
    factors = [0.80, 0.65, 0.50, 0.35, 0.20]
    factor = factors[severity - 1]
    return (img * factor).astype(np.float32)


CORRUPTION_FUNCS: Dict[str, Callable[[np.ndarray, int], np.ndarray]] = {
    "gaussian_noise": apply_gaussian_noise,
    "rotation": apply_rotation,
    "affine_shear": apply_shear,
    "stroke_thickness": apply_stroke_morphology,
    "translation": apply_translation,
    "contrast_attenuation": apply_contrast_attenuation
}


def benchmark_model_robustness(
    model_wrapper: Any,
    test_images: np.ndarray,
    test_labels: np.ndarray,
    n_eval_samples: int = 1000
) -> Dict[str, Any]:
    """
    Evaluates model across 6 corruptions and 5 severity levels on a sample subset.
    """
    np.random.seed(42)
    indices = np.random.choice(len(test_labels), size=min(n_eval_samples, len(test_labels)), replace=False)
    sub_imgs = test_images[indices]
    sub_labels = test_labels[indices]

    robustness_results: Dict[str, Any] = {}

    for corr_name, corr_fn in CORRUPTION_FUNCS.items():
        severities = []
        accuracies = []
        for sev in range(1, 6):
            corrupted_imgs = np.array([corr_fn(img, sev) for img in sub_imgs])

            if hasattr(model_wrapper, "predict_batch_proba"):
                probs = model_wrapper.predict_batch_proba(corrupted_imgs)
            else:
                flat = corrupted_imgs.reshape(len(corrupted_imgs), -1)
                probs = model_wrapper.model.predict_proba(flat)

            preds = np.argmax(probs, axis=1)
            acc = float(accuracy_score(sub_labels, preds))
            severities.append(sev)
            accuracies.append(round(acc * 100.0, 2))

        robustness_results[corr_name] = {
            "severities": severities,
            "accuracies": accuracies,
            "mean_degraded_accuracy": round(float(np.mean(accuracies)), 2),
            "max_drop": round(float(accuracies[0] - accuracies[-1]), 2)
        }

    return robustness_results
