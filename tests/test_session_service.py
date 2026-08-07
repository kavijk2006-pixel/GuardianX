from backend.services.session_service import SessionService
import pytest

def test_create_get_update_delete_session():
    svc = SessionService()
    session = svc.create_session("s1", {"member": {"id": "CAND-004"}})
    assert session["sessionId"] == "s1"
    assert session["questionsAsked"] == 0
    assert session["lastReply"] is None

    got = svc.get_session("s1")
    assert got["sessionId"] == "s1"

    updated = svc.update_session("s1", {"questionsAsked": 5, "lastReply": "foo"})
    assert updated["questionsAsked"] == 5
    assert updated["lastReply"] == "foo"

    svc.delete_session("s1")
    with pytest.raises(KeyError):
        svc.get_session("s1")

def test_session_isolation_and_unknown_handling():
    svc = SessionService()
    a = svc.create_session("a", {"member": {"id": "CAND-004"}})
    b = svc.create_session("b", {"member": {"id": "CAND-004"}})

    svc.update_session("a", {"questionsAsked": 2})
    assert svc.get_session("a")["questionsAsked"] == 2
    assert svc.get_session("b")["questionsAsked"] == 0  # isolation

    with pytest.raises(KeyError):
        svc.update_session("nope", {"questionsAsked": 1})
    with pytest.raises(KeyError):
        svc.get_session("nope")
