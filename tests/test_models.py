"""
DIGITVISION AI — Unit Tests: Model Architecture Invariants
==========================================================
Verifies that all neural architectures and classical wrappers conform to
the DigitVision Model Interface, emit valid probability simplices, and
maintain structural invariants.
"""

import pytest
import numpy as np
from src.models.deep import build_lenet5, build_deep_convnet, DeepModelWrapper
from src.models.classical import (
    build_logistic_regression,
    build_random_forest,
    ClassicalModelWrapper
)


def test_deep_convnet_structure():
    """Verify Deep ConvNet input/output shapes and Grad-CAM layer presence."""
    model = build_deep_convnet()
    assert model.input_shape == (None, 28, 28, 1)
    assert model.output_shape == (None, 10)

    # Invariant: Must contain 'conv_cam' layer for explainable attribution
    layer_names = [l.name for l in model.layers]
    assert "conv_cam" in layer_names


def test_lenet5_structure():
    """Verify classic LeNet-5 structure."""
    model = build_lenet5()
    assert model.input_shape == (None, 28, 28, 1)
    assert model.output_shape == (None, 10)


def test_classical_model_wrapper():
    """Verify classical model wrapper returns valid probability simplex."""
    # Synthetic dataset with 10 classes
    X = np.random.uniform(0.0, 1.0, (50, 784))
    y = np.array([i % 10 for i in range(50)])

    rf = build_random_forest(n_estimators=10)
    rf.fit(X, y)
    wrapper = ClassicalModelWrapper(rf, name="Test-RF")

    sample_img = np.random.uniform(0.0, 1.0, (28, 28)).astype(np.float32)
    probs = wrapper.predict_proba(sample_img)

    assert len(probs) == 10
    assert np.isclose(np.sum(probs), 1.0)
    assert wrapper.is_deep is False
    assert isinstance(wrapper.predict(sample_img), int)
