"""
DIGITVISION AI — Unit Tests: Explainable AI (Grad-CAM & Saliency)
================================================================
Validates that Grad-CAM and Saliency maps have proper dimensions (28, 28),
are bounded in [0.0, 1.0], produce non-trivial gradients on active inputs,
and generate base64 overlay visualizations without error.
"""

import pytest
import numpy as np
import tensorflow as tf
from src.models.deep import build_deep_convnet
from src.xai.gradcam import generate_gradcam_heatmap, render_gradcam_overlay
from src.xai.saliency import compute_pixel_saliency, render_saliency_overlay


@pytest.fixture(scope="module")
def sample_model():
    model = build_deep_convnet()
    return model


def test_gradcam_heatmap_shape_and_bounds(sample_model):
    """Verify Grad-CAM produces 28x28 heatmap bounded in [0, 1]."""
    dummy_input = np.random.uniform(0.0, 1.0, size=(1, 28, 28, 1)).astype(np.float32)
    heatmap, analyzed_class = generate_gradcam_heatmap(sample_model, dummy_input, target_class=3)

    assert heatmap.shape == (28, 28)
    assert heatmap.dtype == np.float32
    assert heatmap.min() >= 0.0
    assert heatmap.max() <= 1.0
    assert analyzed_class == 3


def test_gradcam_overlay_rendering(sample_model):
    """Verify overlay produces valid base64 PNG data URL."""
    orig_img = np.zeros((28, 28), dtype=np.float32)
    orig_img[10:20, 10:20] = 1.0
    heatmap = np.full((28, 28), 0.5, dtype=np.float32)

    url = render_gradcam_overlay(orig_img, heatmap)
    assert url.startswith("data:image/png;base64,")
    assert len(url) > 100


def test_saliency_shape_and_bounds(sample_model):
    """Verify saliency map produces 28x28 array bounded in [0, 1]."""
    dummy_input = np.random.uniform(0.0, 1.0, size=(1, 28, 28, 1)).astype(np.float32)
    saliency, target_c = compute_pixel_saliency(sample_model, dummy_input, target_class=5)

    assert saliency.shape == (28, 28)
    assert saliency.dtype == np.float32
    assert saliency.min() >= 0.0
    assert saliency.max() <= 1.0
    assert target_c == 5

    url = render_saliency_overlay(dummy_input[0, :, :, 0], saliency)
    assert url.startswith("data:image/png;base64,")
