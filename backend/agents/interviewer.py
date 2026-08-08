from typing import Dict, Any, Optional, List


class Interviewer:
    """Deterministic interviewer used for development and testing.
    Decides the next question based on candidate and curriculum context and previous state.
    """

    def __init__(self):
        pass

    def _format_question_from_day(self, day: Dict[str, Any], difficulty: str, role: str) -> str:
        title = day.get("title", "a topic")
        objectives = day.get("objectives", [])
        # Use