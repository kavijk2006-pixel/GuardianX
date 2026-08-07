from typing import Dict, Any, List


class FeedbackGenerator:
    """Generate final feedback from interview evidence.
    Uses only recorded evaluations, conversation history, strengths/gaps collected.
    """

    def __init__(self):
        pass

    def generate(self, session_state: Dict[str, Any]) -> Dict[str, Any]:
        evaluations: List[Dict[str, Any]] = session_state.get("answerEvaluations", [])
        strengths = list({s for ev in evaluations for s in ev.get("strengths", [])})
        gaps = list({g for ev in evaluations for g in ev.get("gaps", [])})

        # Build summary from strengths and gaps and topics covered
        topics = session_state.get("topicsCovered", [])
        summary_parts = []
        if strengths:
            summary_parts.append("Demonstrated strengths: " + ", ".join(strengths))
        if gaps:
            summary_parts.append("Areas to improve: " + ", ".join(gaps))
        if topics:
            summary_parts.append("Interview covered topics: " + ", ".join(topics[:10]))

        summary = "".join([p + ". " for p in summary_parts]) if summary_parts else "Interview completed."

        # Next steps — suggest based on gaps
        next_steps: List[str] = []
        if not gaps:
            next_steps.append("Continue building on demonstrated strengths with a capstone project.")
        else:
            for g in gaps:
                if "observability" in g.lower() or "monitor" in g.lower():
                    next_steps.append("Practice adding monitoring and observability to a RAG pipeline.")
                elif "curriculum objectives" in g.lower() or "example" in g.lower():
                    next_steps.append("Practice mapping technical answers to course objectives with concrete examples.")
                else:
                    next_steps.append(f"Review and practice: {g}")

        return {
            "summary": summary,
            "strengths": strengths,
            "gaps": gaps,
            "next": next_steps,
        }
