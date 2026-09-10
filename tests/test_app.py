import sys
import os
import pytest

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test 1: GET /health returns 200 and valid JSON schema with model metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["application"] == "student-ml-api"
    assert data["application_version"] == "1.1.0"
    assert data["model_version"] == "model-1"

def test_predict_success(client):
    """Test 2: POST /predict with valid input returns 200 and correct prediction."""
    response = client.post("/predict", json={"value": 10})
    assert response.status_code == 200
    data = response.get_json()
    assert data["input"] == 10
    assert data["prediction"] == 20

def test_predict_missing_input(client):
    """Test 3: POST /predict with missing input returns 400."""
    response = client.post("/predict", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_predict_invalid_input(client):
    """Test 4: POST /predict with non-numeric value returns 400."""
    response = client.post("/predict", json={"value": "invalid_string"})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_predict_boolean_input(client):
    """Test 5: POST /predict with boolean value returns 400."""
    response = client.post("/predict", json={"value": True})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
