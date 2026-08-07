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
        # Use the first objective as a seed for a question
        seed = objectives[0] if objectives else "Explain the core ideas"
        q = f"On '{title}' ({day.get('type','')}) — {seed}."
        # personalize by role/experience and difficulty
        if role:
            q = f"As a {role}, {q} Please answer at a {difficulty} level."
        else:
            q = f"{q} Please answer at a {difficulty} level."
        return q

    def decide_next_question(self,
                             candidate_context: Dict[str, Any],
                             curriculum_context: Dict[str, List[Dict[str, Any]]],
                             conversation_history: List[Dict[str, Any]],
                             interview_state: Dict[str, Any],
                             latest_answer_evaluation: Optional[Dict[str, Any]] = None,
                             force_follow_up: bool = False
                             ) -> Dict[str, Any]:
        """Return a structured decision dict.
        Priority:
          1. If latest_answer_evaluation indicates follow_up_needed => follow-up on same topic
          2. Else choose from skipped, repeated, completed, other in that order
          3. Avoid repeating the same day/topic
        """
        role = candidate_context.get("member", {}).get("jobRole", "")
        # avoid repeats
        covered_days = set(interview_state.get("curriculumDaysCovered", []))
        # If follow-up is explicitly requested, create follow-up
        if latest_answer_evaluation and latest_answer_evaluation.get("follow_up_needed") or force_follow_up:
            # ask for clarification on the last topic
            last_topic = interview_state.get("currentTopic")
            difficulty = interview_state.get("currentDifficulty") or "foundation"
            question = f"Quick clarification: {latest_answer_evaluation.get('follow_up_reason','Could you clarify your approach?')}"
            return {
                "question": question,
                "curriculum_day": interview_state.get("currentCurriculumDay"),
                "topic": last_topic,
                "difficulty": difficulty,
                "question_type": "follow_up",
                "is_follow_up": True,
            }

        # selection order
        for kind in ["skipped", "repeated", "completed", "other"]:
            candidates = curriculum_context.get(kind, [])
            for day in candidates:
                if not day:
                    continue
                dnum = day.get("day")
                if dnum in covered_days:
                    continue
                # pick this day
                # difficulty heuristic
                if kind == "skipped":
                    difficulty = "foundation"
                    qtype = "foundation"
                elif kind == "repeated":
                    difficulty = "implementation"
                    qtype = "implementation"
                elif kind == "completed":
                    difficulty = "application"
                    qtype = "application"
                else:
                    difficulty = "concept"
                    qtype = "concept"

                question = self._format_question_from_day(day, difficulty, role)
                return {
                    "question": question,
                    "curriculum_day": dnum,
                    "topic": day.get("title"),
                    "difficulty": difficulty,
                    "question_type": qtype,
                    "is_follow_up": False,
                }

        # fallback: ask about a commonly central day (7 embeddings)
        fallback_day = None
        for d in curriculum_context.get("other", []):
            if d and d.get("day") not in covered_days:
                fallback_day = d
                break
        if not fallback_day and curriculum_context.get("other"):
            fallback_day = curriculum_context.get("other")[0]

        if fallback_day:
            dnum = fallback_day.get("day")
            question = self._format_question_from_day(fallback_day, "concept", role)
            return {
                "question": question,
                "curriculum_day": dnum,
                "topic": fallback_day.get("title"),
                "difficulty": "concept",
                "question_type": "concept",
                "is_follow_up": False,
            }

        # Last resort
        return {
            "question": "Tell me about a technical project you built during the cohort and a key decision you made.",
            "curriculum_day": None,
            "topic": "capstone",
            "difficulty": "application",
            "question_type": "open",
            "is_follow_up": False,
        }
