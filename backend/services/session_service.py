from typing import Dict, Any
from copy import deepcopy


class SessionService:
    def __init__(self):
        # In-memory sessions keyed by sessionId
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, session_id: str, candidate: Dict[str, Any]) -> Dict[str, Any]:
        if session_id in self._sessions:
            raise KeyError(f"Session {session_id} already exists")
        state = {
            "sessionId": session_id,
            "candidate": candidate,
            "conversationHistory": [],
            "questionsAsked": 0,
            "curriculumDaysCovered": [],
            "topicsCovered": [],
            "answerEvaluations": [],
            "strengths": [],
            "gaps": [],
            "currentTopic": None,
            "currentDifficulty": None,
            "questionTypesUsed": [],
            "interviewCompleted": False,
            "lastReply": None,
        }
        self._sessions[session_id] = state
        return deepcopy(state)

    def get_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self._sessions:
            raise KeyError(f"Unknown session {session_id}")
        return deepcopy(self._sessions[session_id])

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        if session_id not in self._sessions:
            raise KeyError(f"Unknown session {session_id}")
        self._sessions[session_id].update(updates)
        return deepcopy(self._sessions[session_id])

    def delete_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]
