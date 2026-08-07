from backend.services.interview_controller import InterviewController
from backend.services.candidate_service import CandidateService
from backend.llm.provider import LLMProvider
import pytest


def test_start_interview_and_first_question():
    controller = InterviewController(llm_provider=LLMProvider(provider="test"))
    cand = CandidateService().get_candidate("CAND-004")
    assert cand is not None

    session = controller.start_interview("int-1", cand)
    assert session["sessionId"] == "int-1"
    # After start, lastReply should be set and questionsAsked >= 1
    assert session["lastReply"] is not None
    assert session["questionsAsked"] >= 1


def test_conversation_flow_and_followups_and_completion_limits():
    controller = InterviewController(llm_provider=LLMProvider(provider="test"))
    cand = CandidateService().get_candidate("CAND-004")
    controller.start_interview("int-flow", cand)

    done = False
    # Provide detailed answers to avoid trivial follow-ups; loop until done or limit
    for i in range(40):
        answer = ("I explain implementation and trade-offs, mention deployment, API, docker, monitoring, "
                  "embeddings, retrieval, vector DB, context, and agents to cover objectives.")
        resp = controller.handle_turn("int-flow", answer)
        assert isinstance(resp.get("reply"), (str, type(None)))
        if resp.get("done"):
            done = True
            feedback = resp.get("feedback")
            # feedback must contain required fields
            assert isinstance(feedback, dict)
            assert "summary" in feedback and "strengths" in feedback and "gaps" in feedback and "next" in feedback
            break

    assert done, "Interview did not complete within expected number of turns"

    s = controller.session_service.get_session("int-flow")
    assert s["questionsAsked"] >= 8, "Did not reach minimum questionsAsked"
    # Confirm at least 4 distinct curriculum days are covered
    covered_days = [d for d in s.get("curriculumDaysCovered", []) if d is not None]
    assert len(set(covered_days)) >= 4, f"Only covered days: {covered_days}"


def test_session_isolation_between_two_interviews():
    controller = InterviewController(llm_provider=LLMProvider(provider="test"))
    cand = CandidateService().get_candidate("CAND-004")
    controller.start_interview("iso-a", cand)
    controller.start_interview("iso-b", cand)

    resp_a = controller.handle_turn("iso-a", "Answer A with implementation and deployment details")
    # iso-b should remain unaffected
    s_b = controller.session_service.get_session("iso-b")
    assert s_b["questionsAsked"] == 1
