"""
Integration Tests for Biotech Production API
"""
import pytest
from starlette.testclient import TestClient


def test_api_health_endpoint(client):
    response = client.get("/production/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["error_boundary_active"] is True
    assert "sara" in data["active_capabilities"]


def test_api_metrics_deterministic_proof(client):
    response = client.get("/production/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["uptime_state"] == "OPERATIONAL"
    assert len(data["deterministic_sha256_verification"]) == 64


def test_api_audit_valid_submission(client):
    payload = {
        "task_id": "T-GOV-F01",
        "candidate_name": "Shravani",
        "capability_name": "Drug Safety Evidence Integration",
        "payload": {
            "drug_name": "IBUPROFEN",
            "adverse_event": "Nausea",
            "subject_id": "SUBJ-4821",
            "is_synthetic": False
        },
        "query_drug": "IBUPROFEN",
        "reported_drugs": ["ASPIRIN", "IBUPROFEN"],
        "is_synthetic": False
    }
    headers = {"X-User-Role": "Auditor"}
    response = client.post("/production/biotech/audit", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_result"] == "PASS"
    assert data["composite_score"] == 100.0


def test_api_audit_fail_closed_rejection(client):
    # Empty drug_name must be rejected
    payload = {
        "task_id": "T-GOV-F01",
        "candidate_name": "Shravani",
        "capability_name": "Drug Safety Evidence Integration",
        "payload": {
            "drug_name": "",
            "adverse_event": "Nausea",
            "subject_id": "SUBJ-4821"
        }
    }
    headers = {"X-User-Role": "Auditor"}
    response = client.post("/production/biotech/audit", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_result"] == "FAIL"
    assert data["schema_strictness_score"] == 0.0


def test_api_unauthorized_role_rejected(client):
    payload = {
        "task_id": "T-GOV-F01",
        "candidate_name": "Shravani",
        "capability_name": "Drug Safety Evidence Integration",
        "payload": {"drug_name": "IBUPROFEN"}
    }
    headers = {"X-User-Role": "UnauthorizedRole"}
    response = client.post("/production/biotech/audit", json=payload, headers=headers)
    assert response.status_code == 403
    assert "FORBIDDEN" in response.json()["message"]


def test_api_token_replay_rejected(client):
    token = "sig-replay-test-unique-token-9988"
    payload = {
        "task_id": "T-GOV-F01",
        "candidate_name": "Sara",
        "capability_name": "Formulation & Stability Evidence Intelligence",
        "payload": {"drug_name": "ADALIMUMAB", "adverse_event": "None"}
    }
    headers = {"X-User-Role": "Auditor", "X-Auth-Token": token}
    
    # First call succeeds
    res1 = client.post("/production/biotech/audit", json=payload, headers=headers)
    assert res1.status_code == 200

    # Replay with same token fails with HTTP 409
    res2 = client.post("/production/biotech/audit", json=payload, headers=headers)
    assert res2.status_code == 409
    assert "REPLAY_REJECTED" in res2.json()["message"]


def test_api_error_boundary_zero_500_on_malformed_input(client):
    # Parikshak Strict Gate: Zero unhandled 500 exceptions on malformed inputs
    headers = {"Content-Type": "application/json", "X-User-Role": "Auditor"}
    malformed_body = "{invalid_json_payload: null, unclosed"
    
    response = client.post("/production/biotech/audit", content=malformed_body, headers=headers)
    # Must NOT be 500! Error boundary returns 400 Bad Request or 422 Unprocessable Entity
    assert response.status_code in [400, 422]
    data = response.json()
    assert data["status"] == "error"
    assert "trace_id" in data
