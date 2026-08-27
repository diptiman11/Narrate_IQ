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




def test_decision_endpoint():
    response = client.get("/decision")

    assert response.status_code == 200

    data = response.json()

    assert "date" in data
    assert "problem" in data
    assert "leading_hypothesis" in data
    assert "confidence_score" in data
    assert "validation_score" in data
    assert "top_segments" in data
    assert "recommendation" in data
    assert "priority" in data
    assert "experiment_status" in data
    assert "experiment_outcome" in data
    assert "historical_reliability" in data


def test_learning_endpoint():
    response = client.get("/learning")

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "hypotheses" in data
    assert isinstance(data["hypotheses"], list)


def test_root_cause_endpoint():
    response = client.get("/root-cause")

    assert response.status_code == 200

    data = response.json()

    assert "date" in data
    assert "count" in data
    assert "graph" in data
    assert isinstance(data["graph"], list)


def test_drilldown_endpoint():
    response = client.get("/drilldown/sales")

    assert response.status_code == 200

    data = response.json()

    assert "date" in data
    assert "count" in data
    assert "results" in data
    assert isinstance(data["results"], list)


def test_decision_endpoint():
    response = client.get("/decision")

    assert response.status_code == 200

    data = response.json()

    assert "date" in data
    assert "problem" in data

    assert "kpi" in data
    assert "leading_hypothesis" in data
    assert "validation" in data

    assert "top_segments" in data
    assert "business_events" in data
    assert "recommendation" in data
    assert "experiment" in data
    assert "historical_learning" in data

    assert (
        "confidence_score"
        in data["leading_hypothesis"]
    )

    assert (
        "validation_score"
        in data["validation"]
    )

    assert isinstance(
        data["top_segments"],
        list,
    )

    assert isinstance(
        data["business_events"],
        list,
    )


def test_learning_endpoint():
    response = client.get("/learning")

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data
    assert "history" in data

    assert isinstance(data["summary"], list)
    assert isinstance(data["history"], list)
