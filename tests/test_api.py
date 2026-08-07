from fastapi.testclient import TestClient
from backend.main import app
from backend.services.candidate_service import CandidateService
import pytest

client = TestClient(app)


def test_api_start_missing_sessionId():
    r = client.post("/api/interview", json={"candidate": {"member": {"id": "CAND-004"}}})
    assert r.status_code == 400
    assert r.json().get("detail") == "Missing sessionId"


def test_api_start_with_candidate_and_turns_and_errors():
    cand = CandidateService().get_candidate("CAND-004")
    assert cand is not None

    # Start interview
    r = client.post("/api/interview", json={"sessionId": "api-1", "candidate": cand})
    assert r.status_code == 200
    data = r.json()
    assert "reply" in data
    assert data.get("done") in (True, False)

    # Invalid empty message
    r2 = client.post("/api/interview", json={"sessionId": "api-1", "message": ""})
    assert r2.status_code == 400
    assert r2.json().get("detail") == "Empty candidate message"

    # Unknown sessionId returns 404
    r3 = client.post("/api/interview", json={"sessionId": "no-such", "message": "hi"})
    assert r3.status_code == 404
    assert r3.json().get("detail") == "Unknown session"


def test_api_full_interview_reaches_completion():
    cand = CandidateService().get_candidate("CAND-004")
    # Start interview
    r = client.post("/api/interview", json={"sessionId": "api-full", "candidate": cand})
    assert r.status_code == 200

    done = False
    for _ in range(40):
        message = ("I provide a complete answer referencing implementation, deployment, docker, API, "
                   "embeddings, retrieval, vector DB, memory, and agents.")
        r = client.post("/api/interview", json={"sessionId": "api-full", "message": message})
        assert r.status_code == 200
        data = r.json()
        if data.get("done"):
            done = True
            feedback = data.get("feedback", {})
            # Final response should follow the feedback schema in technical-spec (summary, strengths, gaps, next)
            assert "summary" in feedback and "strengths" in feedback and "gaps" in feedback and "next" in feedback
            break

    assert done, "API interview did not complete in allotted turns"
