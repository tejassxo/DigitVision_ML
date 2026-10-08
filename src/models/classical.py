"""
DIGITVISION AI — Classical Machine Learning Models
==================================================
Implements classical ML baselines:
1. Multinomial Logistic Regression (L2 regularized)
2. Support Vector Classifier (RBF kernel, calibrated probabilities)
3. Random Forest Classifier (Ensemble decision trees)

All models adhere to the unified DigitVision Model Interface.
"""

import os
import joblib
import numpy as np
from typing import Dict, Any, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier


class ClassicalModelWrapper:
    """Unified wrapper conforming to the DigitVision Model Interface."""
    def __init__(self, model_obj: Any, name: str):
        self.model = model_obj
        self.name = name
        self.is_deep = False

    def predict_proba(self, img_28x28: np.ndarray) -> np.ndarray:
        flat = img_28x28.reshape(1, -1)
        probs = self.model.predict_proba(flat)[0]
        return probs.astype(np.float64)

    def predict(self, img_28x28: np.ndarray) -> int:
        flat = img_28x28.reshape(1, -1)
        return int(self.model.predict(flat)[0])

    def save(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.model, filepath)

    @classmethod
    def load(cls, filepath: str, name: str) -> "ClassicalModelWrapper":
        model_obj = joblib.load(filepath)
        return cls(model_obj, name)


def build_logistic_regression(c_param: float = 1.0, max_iter: int = 400) -> LogisticRegression:
    return LogisticRegression(
        C=c_param,
        max_iter=max_iter,
        solver='lbfgs',
        random_state=42,
        n_jobs=-1
    )


def build_svm_rbf(c_param: float = 5.0, gamma: str = 'scale') -> SVC:
    return SVC(
        C=c_param,
        kernel='rbf',
        gamma=gamma,
        probability=True,
        random_state=42,
        cache_size=500
    )


from sklearn.dummy import DummyClassifier


def build_dummy_baseline(strategy: str = "most_frequent") -> DummyClassifier:
    """Zero-rule baseline classifier that always predicts the majority class."""
    return DummyClassifier(strategy=strategy, random_state=42)


def build_random_forest(n_estimators: int = 100, max_depth: Optional[int] = 20) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42,
        n_jobs=-1
    )


