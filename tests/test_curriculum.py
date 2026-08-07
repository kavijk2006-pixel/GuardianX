from backend.services.curriculum_service import CurriculumService
from backend.services.candidate_service import CandidateService


def test_load_curriculum_and_relevance():
    cur = CurriculumService()
    # Ensure curriculum has days
    assert isinstance(cur.curriculum.get("days", []), list)
    # Pick a real candidate and build context
    cand_svc = CandidateService()
    cand = cand_svc.get_candidate("CAND-004")
    assert cand is not None
    ctx = cand_svc.build_candidate_context(cand)
    rel = cur.get_relevant_topics(ctx)
    # Should return dict with keys
    assert set(rel.keys()) >= {"completed", "skipped", "repeated", "other"}
    # If candidate has completed missions, ensure mapping to days works
    if ctx.get("completed_missions"):
        assert isinstance(rel.get("completed"), list)
