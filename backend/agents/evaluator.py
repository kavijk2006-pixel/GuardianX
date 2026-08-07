from typing import Dict, Any, List, Optional


class Evaluator:
    """Deterministic evaluator implementation for development/testing.
    Evaluates a candidate's answer against the current question and curriculum context.
    """

    def __init__(self):
        pass

    def evaluate(self, question: Dict[str, Any], answer: str, curriculum_day: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Very simple deterministic heuristics for scoring
        # Scores 0-5 based on answer length and presence of keywords from the curriculum objectives
        result = {
            "correctness": 0,
            "understanding": 0,
            "practical": 0,
            "depth": 0,
            "clarity": 0,
            "problem_solving": 0,
            "strengths": [],
            "gaps": [],
            "follow_up_needed": False,
            "follow_up_reason": None,
        }

        if not answer or not answer.strip():
            result["gaps"].append("No answer provided")
            result["follow_up_needed"] = True
            result["follow_up_reason"] = "Please provide an answer to proceed."
            return result

        length = len(answer.split())
        if length < 10:
            score = 1
        elif length < 30:
            score = 2
        elif length < 80:
            score = 3
        else:
            score = 4

        # basic assignment
        result["correctness"] = min(5, score)
        result["understanding"] = min(5, score)
        result["practical"] = 2 if "implementation" in answer.lower() or "code" in answer.lower() else 1
        result["depth"] = min(5, score - (0 if "trade-off" in answer.lower() or "scal" in answer.lower() else 1))
        result["clarity"] = min(5, score)
        result["problem_solving"] = 2 if "debug" in answer.lower() or "fail" in answer.lower() else 1

        # Inspect curriculum objectives for keywords
        keywords = []
        if curriculum_day:
            for obj in curriculum_day.get("objectives", []):
                keywords.extend([w.lower() for w in obj.split() if len(w) > 3])

        matches = sum(1 for k in keywords if k in answer.lower())
        if matches >= 2:
            result["strengths"].append("Referenced curriculum objectives clearly")
            result["understanding"] = min(5, result["understanding"] + 1)
        else:
            result["gaps"].append("Did not reference curriculum objectives directly")
            result["follow_up_needed"] = True
            result["follow_up_reason"] = "Can you tie your answer to the course objectives or give a brief example?"

        # If the answer uses implementation details, boost practical and problem_solving
        if "api" in answer.lower() or "deployment" in answer.lower() or "docker" in answer.lower():
            result["practical"] = min(5, result["practical"] + 2)
            result["problem_solving"] = min(5, result["problem_solving"] + 1)

        return result
