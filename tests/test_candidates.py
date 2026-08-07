from backend.services.candidate_service import CandidateService


def test_load_candidate_cand_004():
    svc = CandidateService()
    cand = svc.get_candidate("CAND-004")
    assert cand is not None
    assert cand.get("member", {}).get("id") == "CAND-004"
