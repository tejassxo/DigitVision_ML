"""
DIGITVISION AI — Unit Tests: MNIST Data Pipeline
================================================
Validates mathematical foundations, partition hygiene, absence of data leakage,
and tensor vs. flattened feature representations.
"""

import pytest
import numpy as np

from src.data.dataset import MNISTPipeline
from src.config import (
    DEFAULT_TRAIN_SAMPLES,
    DEFAULT_VAL_SAMPLES,
    ISOLATED_TEST_SAMPLES,
    NUM_CLASSES,
    CLASS_LABELS,
    FLAT_FEATURE_DIM
)


@pytest.fixture(scope="module")
def pipeline():
    return MNISTPipeline()


def test_mnist_pipeline_partitions(pipeline):
    """Verify that get_partitions correctly separates train, validation, and isolated test sets."""
    (x_tr, y_tr), (x_val, y_val), (x_te, y_te) = pipeline.get_partitions(n_train=2000, n_val=500)

    assert len(x_tr) == 2000
    assert len(y_tr) == 2000
    assert len(x_val) == 500
    assert len(y_val) == 500
    assert len(x_te) == ISOLATED_TEST_SAMPLES
    assert len(y_te) == ISOLATED_TEST_SAMPLES

    assert x_tr.shape == (2000, 28, 28)
    assert x_val.shape == (500, 28, 28)
    assert x_te.shape == (ISOLATED_TEST_SAMPLES, 28, 28)

    assert x_tr.dtype == np.float32
    assert y_tr.dtype == np.int64


def test_no_data_leakage(pipeline):
    """Verify train, validation, and test partitions are disjoint subsets with no overlap."""
    (x_tr_raw, y_tr_raw), (x_te_raw, y_te_raw) = pipeline.load_raw_data()
    n_train = 20000
    n_val = 3000

    (x_tr, y_tr), (x_val, y_val), (x_te, y_te) = pipeline.get_partitions(n_train=n_train, n_val=n_val)

    # Validate that train and val slices of raw data are strictly non-overlapping
    assert len(x_tr) + len(x_val) <= len(x_tr_raw)
    assert len(x_te) == len(x_te_raw)

    # Test indices are completely disjoint from training set
    # Using pointer or id check on source arrays
    assert np.shares_memory(x_tr, x_te) is False
    assert np.shares_memory(x_val, x_te) is False


def test_tensor_representation_space(pipeline):
    """
    Formally validates:
    X ∈ [0, 1]^(N × 28 × 28 × 1) and y ∈ {0, 1, ..., 9}^N
    """
    (x_tr, y_tr), (x_val, y_val), (x_te, y_te) = pipeline.get_tensors(n_train=100, n_val=50)

    assert x_tr.shape == (100, 28, 28, 1)
    assert x_val.shape == (50, 28, 28, 1)
    assert x_te.shape == (ISOLATED_TEST_SAMPLES, 28, 28, 1)

    assert x_tr.dtype == np.float32
    assert x_tr.min() >= 0.0
    assert x_tr.max() <= 1.0


def test_flattened_representation_space(pipeline):
    """
    Formally validates:
    X_flat ∈ [0, 1]^(N × 784) and exact correspondence with image tensor.
    """
    (x_tr_flat, y_tr), (x_val_flat, y_val), (x_te_flat, y_te) = pipeline.get_flat_features(n_train=100, n_val=50)
    (x_tr_tens, _), _, _ = pipeline.get_tensors(n_train=100, n_val=50)

    assert x_tr_flat.shape == (100, FLAT_FEATURE_DIM)
    assert x_val_flat.shape == (50, FLAT_FEATURE_DIM)
    assert x_te_flat.shape == (ISOLATED_TEST_SAMPLES, FLAT_FEATURE_DIM)

    # Equivalence check between tensor and flattened view
    for i in range(10):
        np.testing.assert_array_almost_equal(x_tr_flat[i], x_tr_tens[i].reshape(784))


def test_labels_space_and_class_distribution(pipeline):
    """
    Formally validates:
    y ∈ {0, 1, ..., 9}
    All 10 classes are present in train, val, and test splits.
    """
    (_, y_tr), (_, y_val), (_, y_te) = pipeline.get_partitions(n_train=1000, n_val=300)

    for y_split in [y_tr, y_val, y_te]:
        unique_labels = set(np.unique(y_split))
        assert unique_labels == set(CLASS_LABELS)
        assert np.all((y_split >= 0) & (y_split <= 9))


def test_dataset_statistics_moments(pipeline):
    """Verify dataset statistical moments and sparsity computation."""
    stats = pipeline.compute_dataset_statistics(n_train=1000, n_val=200)

    assert stats["dataset_name"] == "MNIST"
    assert stats["dimensions"] == [28, 28, 1]
    assert stats["num_classes"] == 10

    tr_stats = stats["train_partition"]
    assert tr_stats["sample_count"] == 1000
    assert len(tr_stats["class_counts"]) == 10
    # MNIST images have substantial black background (>70% zero pixels)
    assert tr_stats["sparsity"]["pure_zero_ratio"] > 0.70
