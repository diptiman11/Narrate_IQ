from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "narrate-iq"


def test_analysis_endpoint():
    response = client.get("/analysis")

    assert response.status_code == 200

    data = response.json()

    assert "date" in data
    assert "kpi" in data
    assert "hypotheses" in data
    assert "evidence_validation" in data
    assert "recommendations" in data
    assert "narrative" in data


def test_experiments_endpoint():
    response = client.get("/experiments")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
