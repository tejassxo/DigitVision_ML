"""
DIGITVISION AI — MNIST Dataset Pipeline & Mathematical Foundations
==================================================================
Manages dataset acquisition, partitioning hygiene, mathematical tensor
representations, and feature flattening without test data leakage.

FORMAL MATHEMATICAL DEFINITION:
- Image Tensor Space:   X ∈ [0.0, 1.0]^(N × 28 × 28 × 1), dtype=float32
- Flattened Space:      X_flat ∈ [0.0, 1.0]^(N × 784), dtype=float32
- Label Space:          y ∈ {0, 1, ..., 9}^N, dtype=int64
"""

import hashlib
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import numpy as np

from keras.datasets import mnist
from src.config import (
    RANDOM_SEED,
    DEFAULT_TRAIN_SAMPLES,
    DEFAULT_VAL_SAMPLES,
    RESERVED_TRAIN_SAMPLES,
    ISOLATED_TEST_SAMPLES,
    RAW_TRAIN_SAMPLES,
    RAW_TEST_SAMPLES,
    NUM_CLASSES,
    CLASS_LABELS,
    MNIST_RAW_FILE,
    MNIST_SHA256,
    DATASET_LICENSE,
    DATASET_AUTHORS
)


class MNISTPipeline:
    """
    Standardized, leakage-free data pipeline for the MNIST dataset.
    Enforces strict isolation of the 10,000-sample test partition.
    Guarantees offline reproducibility via local data/raw/mnist.npz caching.
    """
    def __init__(self, seed: int = RANDOM_SEED):
        self.seed = seed
        self._raw_train_imgs: Optional[np.ndarray] = None
        self._raw_train_labels: Optional[np.ndarray] = None
        self._raw_test_imgs: Optional[np.ndarray] = None
        self._raw_test_labels: Optional[np.ndarray] = None

    @staticmethod
    def verify_integrity(filepath: Optional[Path] = None) -> Dict[str, Any]:
        """Verifies SHA-256 cryptographic checksum of local MNIST raw file."""
        target = filepath or MNIST_RAW_FILE
        if not target.exists():
            return {"exists": False, "verified": False, "sha256": None, "filepath": str(target)}
        
        sha256_hash = hashlib.new("sha256")
        with open(target, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        digest = sha256_hash.hexdigest()
        return {
            "exists": True,
            "filepath": str(target),
            "size_bytes": target.stat().st_size,
            "sha256": digest,
            "expected_sha256": MNIST_SHA256,
            "verified": (digest.lower() == MNIST_SHA256.lower()),
            "license": DATASET_LICENSE,
            "curators": DATASET_AUTHORS
        }

    def load_raw_data(self) -> Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]:
        """
        Loads and caches raw uint8 MNIST arrays [0, 255].
        Checks local data/raw/mnist.npz cache first to guarantee offline execution.
        Falls back to upstream Keras mirror if local cache is absent.
        """
        if self._raw_train_imgs is None:
            if MNIST_RAW_FILE.exists():
                with np.load(MNIST_RAW_FILE, allow_pickle=True) as data:
                    x_tr = data["x_train"]
                    y_tr = data["y_train"]
                    x_te = data["x_test"]
                    y_te = data["y_test"]
            else:
                (x_tr, y_tr), (x_te, y_te) = mnist.load_data()
                # Persist exact upstream file locally for offline reproducibility
                import shutil
                keras_cached = Path.home() / ".keras" / "datasets" / "mnist.npz"
                MNIST_RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
                if keras_cached.exists():
                    shutil.copyfile(keras_cached, MNIST_RAW_FILE)
                else:
                    np.savez_compressed(MNIST_RAW_FILE, x_train=x_tr, y_train=y_tr, x_test=x_te, y_test=y_te)

            self._raw_train_imgs = x_tr
            self._raw_train_labels = y_tr.astype(np.int64)
            self._raw_test_imgs = x_te
            self._raw_test_labels = y_te.astype(np.int64)
        return (self._raw_train_imgs, self._raw_train_labels), (self._raw_test_imgs, self._raw_test_labels)

    def get_reserved_pool(
        self,
        n_train: int = DEFAULT_TRAIN_SAMPLES,
        n_val: int = DEFAULT_VAL_SAMPLES
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns the reserved/unused training pool (x_train[n_train+n_val:], y_train[n_train+n_val:]).
        Normalized to float32 [0.0, 1.0]. Totaling 37,000 samples by default.
        """
        (x_tr_raw, y_tr_raw), _ = self.load_raw_data()
        start_idx = n_train + n_val
        x_unused = (x_tr_raw[start_idx:] / 255.0).astype(np.float32)
        y_unused = y_tr_raw[start_idx:]
        return x_unused, y_unused

    def get_partitions(
        self,
        n_train: int = DEFAULT_TRAIN_SAMPLES,
        n_val: int = DEFAULT_VAL_SAMPLES
    ) -> Tuple[
        Tuple[np.ndarray, np.ndarray],
        Tuple[np.ndarray, np.ndarray],
        Tuple[np.ndarray, np.ndarray]
    ]:
        """
        Splits MNIST into normalized float32 partitions:
        - Training:   (n_train, 28, 28) in [0.0, 1.0]
        - Validation: (n_val, 28, 28) in [0.0, 1.0]
        - Test:       (10000, 28, 28) in [0.0, 1.0] — STRICTLY ISOLATED
        """
        (x_tr_raw, y_tr_raw), (x_te_raw, y_te_raw) = self.load_raw_data()

        # Normalize to float32 [0.0, 1.0]
        x_tr_norm = (x_tr_raw / 255.0).astype(np.float32)
        x_te_norm = (x_te_raw / 255.0).astype(np.float32)

        # Enforce partition bounds
        total_train_available = len(y_tr_raw)
        if n_train + n_val > total_train_available:
            raise ValueError(f"Requested train ({n_train}) + val ({n_val}) exceeds total available ({total_train_available}).")

        # Partitioning
        x_train = x_tr_norm[:n_train]
        y_train = y_tr_raw[:n_train]

        x_val = x_tr_norm[n_train:n_train + n_val]
        y_val = y_tr_raw[n_train:n_train + n_val]

        x_test = x_te_norm
        y_test = y_te_raw

        return (x_train, y_train), (x_val, y_val), (x_test, y_test)

    def get_tensors(
        self,
        n_train: int = DEFAULT_TRAIN_SAMPLES,
        n_val: int = DEFAULT_VAL_SAMPLES
    ) -> Tuple[
        Tuple[np.ndarray, np.ndarray],
        Tuple[np.ndarray, np.ndarray],
        Tuple[np.ndarray, np.ndarray]
    ]:
        """
        Returns data in 4D CNN Tensor representation: (N, 28, 28, 1).
        X ∈ [0.0, 1.0]^(N × 28 × 28 × 1), y ∈ {0, ..., 9}^N.
        """
        (x_tr, y_tr), (x_v, y_v), (x_te, y_te) = self.get_partitions(n_train, n_val)
        return (
            (np.expand_dims(x_tr, -1), y_tr),
            (np.expand_dims(x_v, -1), y_v),
            (np.expand_dims(x_te, -1), y_te)
        )

    def get_flat_features(
        self,
        n_train: int = DEFAULT_TRAIN_SAMPLES,
        n_val: int = DEFAULT_VAL_SAMPLES
    ) -> Tuple[
        Tuple[np.ndarray, np.ndarray],
        Tuple[np.ndarray, np.ndarray],
        Tuple[np.ndarray, np.ndarray]
    ]:
        """
        Returns data in 2D Flattened Feature representation: (N, 784).
        X_flat ∈ [0.0, 1.0]^(N × 784), y ∈ {0, ..., 9}^N.
        """
        (x_tr, y_tr), (x_v, y_v), (x_te, y_te) = self.get_partitions(n_train, n_val)
        return (
            (x_tr.reshape(len(x_tr), 784), y_tr),
            (x_v.reshape(len(x_v), 784), y_v),
            (x_te.reshape(len(x_te), 784), y_te)
        )

    def compute_dataset_statistics(
        self,
        n_train: int = DEFAULT_TRAIN_SAMPLES,
        n_val: int = DEFAULT_VAL_SAMPLES
    ) -> Dict[str, Any]:
        """
        Computes formal statistical distributions, class frequencies,
        sparsity metrics, and pixel moments across all partitions.
        """
        (x_tr, y_tr), (x_v, y_v), (x_te, y_te) = self.get_partitions(n_train, n_val)
        x_res, y_res = self.get_reserved_pool(n_train, n_val)

        def get_split_stats(imgs: np.ndarray, labels: np.ndarray, name: str) -> Dict[str, Any]:
            class_counts = {c: int(np.sum(labels == c)) for c in range(NUM_CLASSES)}
            total = len(labels)
            class_props = {c: round(float(class_counts[c] / total), 4) for c in range(NUM_CLASSES)}
            zero_pixel_ratio = float(np.mean(imgs == 0.0))
            active_pixel_ratio = float(np.mean(imgs > 0.05))

            return {
                "partition_name": name,
                "sample_count": total,
                "class_counts": class_counts,
                "class_proportions": class_props,
                "pixel_moments": {
                    "min": float(np.min(imgs)),
                    "max": float(np.max(imgs)),
                    "mean": round(float(np.mean(imgs)), 5),
                    "std": round(float(np.std(imgs)), 5)
                },
                "sparsity": {
                    "pure_zero_ratio": round(zero_pixel_ratio, 4),
                    "active_stroke_ratio": round(active_pixel_ratio, 4)
                }
            }

        return {
            "dataset_name": "MNIST",
            "dimensions": [28, 28, 1],
            "num_classes": NUM_CLASSES,
            "train_partition": get_split_stats(x_tr, y_tr, "Train"),
            "val_partition": get_split_stats(x_v, y_v, "Validation"),
            "reserved_partition": get_split_stats(x_res, y_res, "Reserved Training Pool"),
            "test_partition": get_split_stats(x_te, y_te, "Isolated Test")
        }
