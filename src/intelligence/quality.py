"""
DIGITVISION AI — Input-Quality Intelligence
===========================================
Analyzes raw and preprocessed stroke inputs for topological anomalies,
insufficient contrast, stroke fragmentation, noise artifacts, and centering quality.
Emits a composite quality score [0, 100] and actionable validation flags.
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Tuple


def assess_input_quality(
    preprocessed_img: np.ndarray,
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Assesses the physical and topological quality of a handwritten input digit.

    Args:
        preprocessed_img: Canonical 28x28 float32 array in [0.0, 1.0].
        metadata: Diagnostic metadata returned by canonical_preprocess.

    Returns:
        Dict with quality score, telemetry metrics, and validation flags.
    """
    if metadata.get("is_empty", False):
        return {
            "quality_score": 0.0,
            "quality_band": "INVALID_EMPTY",
            "is_valid": False,
            "reasons": ["Canvas is blank. No stroke detected."],
            "stroke_pixel_count": 0,
            "bounding_box_coverage": 0.0,
            "aspect_ratio": 0.0,
            "centroid_offset": 0.0,
            "sharpness": 0.0,
            "noise_ratio": 0.0,
            "warnings": ["EMPTY_CANVAS"]
        }

    warnings: List[str] = []
    reasons: List[str] = []

    # 1. Active stroke pixel count (intensity > 0.05)
    active_mask = (preprocessed_img > 0.05).astype(np.uint8)
    stroke_pixels = int(np.count_nonzero(active_mask))

    # 2. Bounding box coverage
    bbox = metadata.get("bbox", {})
    if bbox:
        bbox_w = bbox.get("w", 0)
        bbox_h = bbox.get("h", 0)
        aspect_ratio = float(bbox_w / max(1, bbox_h))
    else:
        coords = cv2.findNonZero(active_mask)
        if coords is not None and len(coords) > 0:
            _, _, bbox_w, bbox_h = cv2.boundingRect(coords)
            aspect_ratio = float(bbox_w / max(1, bbox_h))
        else:
            bbox_w, bbox_h, aspect_ratio = 0, 0, 1.0

    canvas_area = 28.0 * 28.0
    coverage = float(stroke_pixels / canvas_area)

    # 3. Centroid offset from optimal center (13.5, 13.5)
    target_cx, target_cy = 13.5, 13.5
    final_centroid = metadata.get("centroid_final", (13.5, 13.5))
    centroid_dist = float(np.sqrt((final_centroid[0] - target_cx)**2 + (final_centroid[1] - target_cy)**2))

    # 4. Sharpness via variance of Laplacian
    img_uint8 = (preprocessed_img * 255.0).astype(np.uint8)
    laplacian = cv2.Laplacian(img_uint8, cv2.CV_64F)
    sharpness = float(laplacian.var())

    # 5. Connected component analysis / Noise ratio
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(active_mask, connectivity=8)
    # Label 0 is background; labels 1..num_labels-1 are foreground components
    if num_labels > 1:
        component_areas = stats[1:, cv2.CC_STAT_AREA]
        max_area = float(np.max(component_areas))
        total_fg = float(np.sum(component_areas))
        noise_pixels = total_fg - max_area
        noise_ratio = float(noise_pixels / max(1.0, total_fg))
    else:
        noise_ratio = 0.0

    # Validation and warning checks
    if stroke_pixels < 18:
        warnings.append("VERY_SPARSE_STROKE")
        reasons.append(f"Stroke pixel count ({stroke_pixels}) is too low for reliable digit classification.")

    if stroke_pixels > 380:
        warnings.append("EXCESSIVE_STROKE_WIDTH")
        reasons.append("Drawing fills excessive canvas area; stroke thickness exceeds normal distribution.")

    if centroid_dist > 4.5:
        warnings.append("SIGNIFICANT_OFF_CENTER")
        reasons.append("Digit centroid deviates significantly from optical center.")

    if noise_ratio > 0.25:
        warnings.append("HIGH_FRAGMENTATION")
        reasons.append("Multiple disconnected stroke fragments or speckle noise detected.")

    if sharpness < 15.0:
        warnings.append("LOW_CONTRAST_OR_BLUR")

    # Composite Quality Score Calculation [0, 100]
    # Penalize for extreme sparsity, excessive thickness, heavy noise, extreme aspect ratio
    score = 100.0

    # Penalize low stroke counts
    if stroke_pixels < 40:
        score -= (40 - stroke_pixels) * 1.5

    # Penalize heavy fills
    if stroke_pixels > 250:
        score -= (stroke_pixels - 250) * 0.25

    # Penalize fragmentation / noise
    score -= noise_ratio * 40.0

    # Penalize centroid deviation
    score -= centroid_dist * 3.0

    # Aspect ratio penalty if extreme (unless thin digit like '1')
    if aspect_ratio > 3.0:
        score -= min(25.0, (aspect_ratio - 3.0) * 10.0)

    score = float(np.clip(score, 0.0, 100.0))

    is_valid = (score >= 35.0) and (stroke_pixels >= 15) and (noise_ratio < 0.45)

    if not is_valid and not reasons:
        reasons.append(f"Input quality score ({score:.1f}/100) below acceptable inference threshold.")

    if score >= 75.0:
        quality_band = "OPTIMAL"
    elif score >= 50.0:
        quality_band = "ACCEPTABLE"
    elif score >= 35.0:
        quality_band = "MARGINAL"
    else:
        quality_band = "DEGRADED"

    return {
        "quality_score": round(score, 2),
        "quality_band": quality_band,
        "is_valid": is_valid,
        "reasons": reasons,
        "stroke_pixel_count": stroke_pixels,
        "bounding_box_coverage": round(coverage, 4),
        "aspect_ratio": round(aspect_ratio, 3),
        "centroid_offset": round(centroid_dist, 3),
        "sharpness": round(sharpness, 2),
        "noise_ratio": round(noise_ratio, 4),
        "num_components": int(num_labels - 1),
        "warnings": warnings
    }
