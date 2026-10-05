"""
DIGITVISION AI — Unit Tests: Canonical Preprocessing Invariant
==============================================================
Validates that the single authoritative preprocessing pipeline strictly preserves
the MNIST invariant: aspect-ratio preserved, centroid aligned to (13.5, 13.5),
and values strictly normalized in [0.0, 1.0].
"""

import pytest
import numpy as np
from src.preprocessing.canonical import (
    canonical_preprocess,
    compute_center_of_mass,
    detect_and_normalize_contrast,
    decode_image_input
)


def test_empty_canvas():
    """Verify empty/blank canvas is identified and returns blank 28x28 array."""
    blank = np.zeros((100, 100), dtype=np.uint8)
    processed, meta = canonical_preprocess(blank)

    assert processed.shape == (28, 28)
    assert processed.dtype == np.float32
    assert np.all(processed == 0.0)
    assert meta["is_empty"] is True


def test_output_bounds_and_dtype():
    """Verify output pixel intensities are strictly in [0.0, 1.0] and float32."""
    canvas = np.zeros((150, 150), dtype=np.uint8)
    # Draw a vertical line simulating digit '1'
    canvas[20:130, 70:80] = 255

    processed, meta = canonical_preprocess(canvas)
    assert processed.shape == (28, 28)
    assert processed.dtype == np.float32
    assert processed.min() >= 0.0
    assert processed.max() <= 1.0
    assert meta["is_empty"] is False


def test_translation_invariance_centroid_alignment():
    """
    Verify translation invariance: A digit drawn at top-left vs bottom-right
    is centered such that its final center of mass is within 1 pixel of (13.5, 13.5).
    """
    # Digit patch (20x20 circle/square)
    patch = np.zeros((20, 20), dtype=np.uint8)
    patch[4:16, 4:16] = 255

    # Place in top-left
    canvas_tl = np.zeros((120, 120), dtype=np.uint8)
    canvas_tl[10:30, 10:30] = patch

    # Place in bottom-right
    canvas_br = np.zeros((120, 120), dtype=np.uint8)
    canvas_br[80:100, 80:100] = patch

    proc_tl, meta_tl = canonical_preprocess(canvas_tl)
    proc_br, meta_br = canonical_preprocess(canvas_br)

    cx_tl, cy_tl = meta_tl["centroid_final"]
    cx_br, cy_br = meta_br["centroid_final"]

    # Target is (13.5, 13.5)
    assert abs(cx_tl - 13.5) < 1.0
    assert abs(cy_tl - 13.5) < 1.0
    assert abs(cx_br - 13.5) < 1.0
    assert abs(cy_br - 13.5) < 1.0


def test_contrast_normalization():
    """Verify dark-on-light (black ink on white paper) is inverted to white-on-black."""
    white_paper = np.full((100, 100), 255, dtype=np.uint8)
    # Black stroke
    white_paper[30:70, 45:55] = 0

    inverted = detect_and_normalize_contrast(white_paper)
    # Background should now be near 0, stroke near 255
    assert inverted[0, 0] == 0
    assert inverted[50, 50] == 255
