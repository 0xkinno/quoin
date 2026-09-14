import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

def test_api_policies_get(client):
    res = client.get("/api/policies")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ACTIVE"
    assert data["generation"] >= 17

def test_api_requests_evaluate_and_commit(client):
    # 1. Evaluate request
    eval_payload = {
        "request_id": "req_api_test_01",
        "tenant_id": "agency_operations",
        "client_tier": "standard",
        "amount": 350.0,
        "action": "apply_discount",
        "invoice_id": "inv_test",
        "discount_percentage": 7.0
    }
    eval_res = client.post("/api/requests/evaluate", json=eval_payload)
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert eval_data["allowed"] is True
    receipt = eval_data["receipt"]
    assert receipt is not None

    # 2. Commit request
    commit_payload = {
        "receipt": receipt,
        "request_payload": eval_payload,
        "proposal": eval_data["proposal"]
    }
    commit_res = client.post("/api/requests/commit", json=commit_payload)
    assert commit_res.status_code == 200
    commit_data = commit_res.json()
    assert commit_data["committed"] is True
    assert commit_data["status"] == "COMMITTED"
