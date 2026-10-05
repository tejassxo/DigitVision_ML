"""
DIGITVISION AI — Unit Tests: Canonical Preprocessing Invariant
==============================================================
Validates that the single authoritative preprocessing pipeline strictly preserves
the MNIST invariant across all input modalities:
- Input dimensions & shapes (2D, 3D RGB, 4D RGBA)
- Grayscale conversion
- Background/contrast inversion
- Normalization [0.0, 1.0] and float32 dtype
- Foreground detection & bounding box computation
- Center of mass alignment to canonical (13.5, 13.5)
- Empty / blank canvas edge cases
- Noisy canvas edge cases
- Oversized inputs (e.g., 512x512)
- Tiny inputs (e.g., 10x10)
- Already-28x28 native inputs
- Tensor output shape (1, 28, 28, 1) via canonical_preprocess_tensor
"""

import pytest
import numpy as np
import cv2
from PIL import Image

from src.preprocessing.canonical import (
    canonical_preprocess,
    canonical_preprocess_tensor,
    compute_center_of_mass,
    detect_and_normalize_contrast,
    decode_image_input
)
from src.config import (
    CANONICAL_CANVAS_SHAPE,
    CANONICAL_CENTROID_TARGET,
    TENSOR_OUTPUT_SHAPE
)


def test_input_dimensions_and_channels():
    """Verify preprocessing handles 2D, 3D RGB, and 4D RGBA inputs seamlessly."""
    # 1. 2D grayscale
    img_2d = np.zeros((100, 100), dtype=np.uint8)
    img_2d[20:80, 45:55] = 255
    res_2d, meta_2d = canonical_preprocess(img_2d)
    assert res_2d.shape == CANONICAL_CANVAS_SHAPE
    assert res_2d.dtype == np.float32

    # 2. 3D RGB
    img_rgb = np.zeros((100, 100, 3), dtype=np.uint8)
    img_rgb[20:80, 45:55, :] = [255, 255, 255]
    res_rgb, meta_rgb = canonical_preprocess(img_rgb)
    assert res_rgb.shape == CANONICAL_CANVAS_SHAPE
    assert res_rgb.dtype == np.float32

    # 3. 4D RGBA
    img_rgba = np.zeros((100, 100, 4), dtype=np.uint8)
    img_rgba[20:80, 45:55, :] = [255, 255, 255, 255]
    res_rgba, meta_rgba = canonical_preprocess(img_rgba)
    assert res_rgba.shape == CANONICAL_CANVAS_SHAPE
    assert res_rgba.dtype == np.float32


def test_grayscale_conversion():
    """Verify color inputs (e.g., green/red strokes) are properly converted to grayscale."""
    color_img = np.zeros((100, 100, 3), dtype=np.uint8)
    # Pure green stroke
    color_img[30:70, 40:60] = [0, 255, 0]
    decoded = decode_image_input(color_img)
    assert decoded.ndim == 2
    assert decoded.shape == (100, 100)
    # Green in Rec. 601 grayscale is ~ 0.587 * 255 = ~150
    assert 140 <= decoded[50, 50] <= 160


def test_inversion_and_contrast_normalization():
    """Verify light-on-dark is preserved, and dark-on-light is inverted to MNIST standard."""
    # Case A: Dark background (0), white stroke (255) -> should NOT invert
    dark_bg = np.zeros((80, 80), dtype=np.uint8)
    dark_bg[20:60, 35:45] = 255
    norm_dark = detect_and_normalize_contrast(dark_bg)
    assert norm_dark[0, 0] == 0
    assert norm_dark[40, 40] == 255

    # Case B: White background (255), black stroke (0) -> MUST invert
    white_bg = np.full((80, 80), 255, dtype=np.uint8)
    white_bg[20:60, 35:45] = 0
    norm_white = detect_and_normalize_contrast(white_bg)
    assert norm_white[0, 0] == 0
    assert norm_white[40, 40] == 255


def test_normalization_bounds_and_dtype():
    """Verify output pixel intensities are strictly in [0.0, 1.0] and float32 without NaNs."""
    canvas = np.zeros((120, 120), dtype=np.uint8)
    cv2.circle(canvas, (60, 60), 30, 255, 4)

    processed, meta = canonical_preprocess(canvas)
    assert processed.dtype == np.float32
    assert np.all(np.isfinite(processed))
    assert processed.min() >= 0.0
    assert processed.max() <= 1.0
    assert processed.max() > 0.5  # Strong stroke presence


def test_bounding_box_extraction():
    """Verify bounding box accurately isolates the stroke coordinate bounds."""
    canvas = np.zeros((100, 100), dtype=np.uint8)
    # Draw stroke strictly in region x: [30, 60], y: [20, 70]
    canvas[20:70, 30:60] = 255

    processed, meta = canonical_preprocess(canvas)
    bbox = meta["bbox"]
    assert bbox is not None
    assert bbox["x"] == 30
    assert bbox["y"] == 20
    assert bbox["w"] == 30
    assert bbox["h"] == 50


def test_centering_and_centroid_alignment():
    """
    Verify translation invariance: Digit drawn at top-left vs bottom-right
    is aligned such that center-of-mass is within 1.0px of target (13.5, 13.5).
    """
    patch = np.zeros((24, 24), dtype=np.uint8)
    cv2.circle(patch, (12, 12), 8, 255, -1)

    # Top-left placement
    canvas_tl = np.zeros((120, 120), dtype=np.uint8)
    canvas_tl[5:29, 5:29] = patch

    # Bottom-right placement
    canvas_br = np.zeros((120, 120), dtype=np.uint8)
    canvas_br[85:109, 85:109] = patch

    proc_tl, meta_tl = canonical_preprocess(canvas_tl)
    proc_br, meta_br = canonical_preprocess(canvas_br)

    cx_tl, cy_tl = meta_tl["centroid_final"]
    cx_br, cy_br = meta_br["centroid_final"]

    target_x, target_y = CANONICAL_CENTROID_TARGET
    assert abs(cx_tl - target_x) < 1.0
    assert abs(cy_tl - target_y) < 1.0
    assert abs(cx_br - target_x) < 1.0
    assert abs(cy_br - target_y) < 1.0


def test_empty_image():
    """Verify blank / all-zero or all-white canvas is identified as empty without crashing."""
    blank_zeros = np.zeros((80, 80), dtype=np.uint8)
    proc_zero, meta_zero = canonical_preprocess(blank_zeros)
    assert meta_zero["is_empty"] is True
    assert proc_zero.shape == (28, 28)
    assert np.all(proc_zero == 0.0)

    blank_white = np.full((80, 80), 255, dtype=np.uint8)
    proc_white, meta_white = canonical_preprocess(blank_white)
    assert meta_white["is_empty"] is True
    assert np.all(proc_white == 0.0)


def test_noisy_image():
    """Verify background noise is suppressed and prominent digit stroke is extracted."""
    np.random.seed(42)
    # Add random low-amplitude noise
    noisy_canvas = np.random.randint(0, 15, size=(120, 120), dtype=np.uint8)
    # Add clear digit stroke
    noisy_canvas[30:90, 55:65] = 255

    proc, meta = canonical_preprocess(noisy_canvas, threshold=25)
    assert meta["is_empty"] is False
    assert proc.shape == (28, 28)
    # Corners of processed canvas should be clean background
    assert proc[0, 0] == 0.0
    assert proc[27, 27] == 0.0


def test_oversized_image():
    """Verify large high-resolution images (e.g., 512x512) are downscaled properly."""
    large_canvas = np.zeros((512, 512), dtype=np.uint8)
    cv2.putText(large_canvas, "8", (150, 400), cv2.FONT_HERSHEY_SIMPLEX, 12, 255, 20)

    proc, meta = canonical_preprocess(large_canvas)
    assert meta["is_empty"] is False
    assert proc.shape == (28, 28)
    assert proc.dtype == np.float32
    assert meta["raw_shape"] == (512, 512)


def test_tiny_image():
    """Verify small images (e.g., 10x10) are upscaled into the 28x28 canvas without distortion."""
    tiny_canvas = np.zeros((10, 10), dtype=np.uint8)
    tiny_canvas[2:8, 4:6] = 255

    proc, meta = canonical_preprocess(tiny_canvas)
    assert meta["is_empty"] is False
    assert proc.shape == (28, 28)
    assert proc.max() > 0.5


def test_already_28x28_image():
    """Verify images that are natively 28x28 are appropriately normalized and centered."""
    native_28 = np.zeros((28, 28), dtype=np.uint8)
    native_28[4:24, 12:16] = 255

    proc, meta = canonical_preprocess(native_28)
    assert proc.shape == (28, 28)
    assert meta["raw_shape"] == (28, 28)
    assert meta["is_empty"] is False


def test_canonical_preprocess_tensor():
    """Verify canonical_preprocess_tensor strictly returns shape (1, 28, 28, 1) float32."""
    canvas = np.zeros((100, 100), dtype=np.uint8)
    canvas[20:80, 45:55] = 255

    tensor, meta = canonical_preprocess_tensor(canvas)
    assert tensor.shape == TENSOR_OUTPUT_SHAPE
    assert tensor.dtype == np.float32
    assert tensor.min() >= 0.0
    assert tensor.max() <= 1.0

    # Also test empty canvas with tensor wrapper
    empty_tensor, empty_meta = canonical_preprocess_tensor(np.zeros((50, 50), dtype=np.uint8))
    assert empty_tensor.shape == TENSOR_OUTPUT_SHAPE
    assert empty_tensor.dtype == np.float32
    assert np.all(empty_tensor == 0.0)
    assert empty_meta["is_empty"] is True
