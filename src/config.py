"""
DIGITVISION AI — Centralized System Configuration
=================================================
Centralized parameters for dataset pipelines, canonical preprocessing invariants,
training/evaluation batch sizes, random seeds, and directory path topologies.
Prevents magic numbers across the entire codebase.
"""

import os
from pathlib import Path
from typing import Tuple, List

# 1. REPRODUCIBILITY & SEEDS
RANDOM_SEED: int = 42

# 2. DATASET SPECIFICATIONS
DATASET_NAME: str = "MNIST"
DATASET_SOURCE: str = "Yann LeCun, Corinna Cortes, Christopher Burges (NIST Special Database 19/3)"
TOTAL_MNIST_SAMPLES: int = 70000
RAW_TRAIN_SAMPLES: int = 60000
RAW_TEST_SAMPLES: int = 10000

# Partitions
DEFAULT_TRAIN_SAMPLES: int = 20000
DEFAULT_VAL_SAMPLES: int = 3000
ISOLATED_TEST_SAMPLES: int = 10000

# Classes
NUM_CLASSES: int = 10
CLASS_LABELS: List[int] = list(range(10))
CLASS_NAMES: List[str] = [str(i) for i in range(10)]

# 3. CANONICAL PREPROCESSING INVARIANT PARAMETERS
CANONICAL_CANVAS_SHAPE: Tuple[int, int] = (28, 28)
CANONICAL_INNER_BOX_SIZE: int = 20
CANONICAL_CENTROID_TARGET: Tuple[float, float] = (13.5, 13.5)
TENSOR_OUTPUT_SHAPE: Tuple[int, int, int, int] = (1, 28, 28, 1)
FLAT_FEATURE_DIM: int = 784
PIXEL_MIN: float = 0.0
PIXEL_MAX: float = 1.0
STROKE_DETECTION_THRESHOLD: int = 25

# 4. TRAINING & INFERENCE HYPERPARAMETERS
BATCH_SIZE_TRAIN: int = 256
BATCH_SIZE_EVAL: int = 256
DEFAULT_EPOCHS: int = 4
DEFAULT_LEARNING_RATE: float = 1e-3

# 5. INPUT QUALITY THRESHOLDS
MIN_STROKE_PIXELS: int = 18
MAX_STROKE_PIXELS: int = 380
MAX_CENTROID_DEVIATION: float = 4.5
MAX_NOISE_RATIO: float = 0.40
MIN_QUALITY_SCORE_VALID: float = 35.0

# 6. UNCERTAINTY & DECISION BOUNDARIES
HIGH_CONFIDENCE_THRESHOLD: float = 0.85
HIGH_CONFIDENCE_MARGIN: float = 0.60
HIGH_CONFIDENCE_ENTROPY_BITS: float = 0.80
MODERATE_CONFIDENCE_THRESHOLD: float = 0.50
MODERATE_CONFIDENCE_MARGIN: float = 0.20

# 7. PATH TOPOLOGY
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"

ARTIFACTS_DIR: Path = PROJECT_ROOT / "artifacts"
ARTIFACTS_DATA_DIR: Path = ARTIFACTS_DIR / "data"

EXPERIMENTS_DIR: Path = PROJECT_ROOT / "experiments"
MODELS_DIR: Path = EXPERIMENTS_DIR / "models"
METRICS_DIR: Path = EXPERIMENTS_DIR / "metrics"
FIGURES_DIR: Path = EXPERIMENTS_DIR / "figures"
FAILURES_DIR: Path = EXPERIMENTS_DIR / "failures"

DOCS_DIR: Path = PROJECT_ROOT / "docs"
PRESENTATION_DIR: Path = PROJECT_ROOT / "src" / "presentation"

# Ensure all critical runtime directories exist
for directory in [
    DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR,
    ARTIFACTS_DIR, ARTIFACTS_DATA_DIR,
    EXPERIMENTS_DIR, MODELS_DIR, METRICS_DIR, FIGURES_DIR, FAILURES_DIR,
    DOCS_DIR, PRESENTATION_DIR
]:
    directory.mkdir(parents=True, exist_ok=True)
