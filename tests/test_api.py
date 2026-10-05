"""
DIGITVISION AI — Unit Tests: REST API Endpoints
================================================
Validates health check, model catalog listing, and rejection handling
via FastAPI TestClient.
"""

import pytest
import base64
import numpy as np
from fastapi.testclient import TestClient
from src.app.server import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_api_health(client):
    """Verify health endpoint returns 200 and expected schema."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "loaded_models" in data


def test_api_models(client):
    """Verify model listing endpoint returns model catalog."""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) >= 3


def test_api_predict_empty_canvas(client):
    """Verify inference gracefully handles empty canvas with REJECTED_INPUT_QUALITY."""
    # Blank 28x28 dummy image encoded as base64
    import cv2
    blank = np.zeros((28, 28), dtype=np.uint8)
    _, encoded = cv2.imencode('.png', blank)
    b64_str = base64.b64encode(encoded).decode('utf-8')

    response = client.post("/api/predict", json={
        "image": f"data:image/png;base64,{b64_str}",
        "model_id": "DigitVision-DeepConvNet",
        "generate_xai": False
    })
    # If models are loaded, it will return 200 with rejection telemetry
    if response.status_code == 200:
        data = response.json()
        assert data["decision"]["status"] == "REJECTED_INPUT_QUALITY"
        assert data["quality_audit"]["is_valid"] is False
    else:
        # If models are still training, status 503 is expected
        assert response.status_code == 503
