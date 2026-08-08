from typing import Dict, Any, Optional, List
from backend.llm.provider import LLMProvider


class Interviewer:
    """AI Interviewer agent that generates persona-driven, human-sounding technical questions
    and adaptive follow-ups tailored to candidate experience and curriculum context.
    """

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider or LLMProvider()

    def _generate_question_prompt(self, candidate_context: Dict[str, Any], day: Dict[str, Any], difficulty: str, is_first: bool = False) -> str:
        member = candidate_context.get("member", {})
        name = member.get("name", "Candidate")
        role = member.get("jobRole", "Software Engineer")
        skills = member.get("skills", [])
        resume_summary = member.get("resumeSummary", "") or member.get("resumeText", "")
        title = day.get("title", "Technical Architecture")
        objectives = day.get("objectives", [])
        obj_text = ", ".join(objectives[:2]) if objectives else "core engineering principles"

        skills_str = f" with expertise in {', '.join(skills[:3])}" if skills else ""

        if is_first:
            if resume_summary:
                snippet = (resume_summary[:120] + "...") if len(resume_summary) > 120 else resume_summary
                return (
                    f"Hello {name}! Welcome to your technical interview. I reviewed your resume highlighting: '{snippet}'. "
                    f"Given your target role as a {role}{skills_str}, let's begin with {title}. "
                    f"Could you walk me through your experience with {obj_text}?"
                )
            return (
                f"Hello {name}! Welcome to your technical interview today. Given your background as a {role}{skills_str}, "
                f"let's begin with {title}. Could you walk me through your experience with {obj_text} and how you apply it in practice?"
            )
        
        return (
            f"Moving on to {title}: as a {role}{skills_str}, how do you approach {obj_text}? "
            f"Please share a concrete architectural decision or implementation example."
        )


    def decide_next_question(self,
                             candidate_context: Dict[str, Any],
                             curriculum_context: Dict[str, List[Dict[str, Any]]],
                             conversation_history: List[Dict[str, Any]],
                             interview_state: Dict[str, Any],
                             latest_answer_evaluation: Optional[Dict[str, Any]] = None,
                             force_follow_up: bool = False
                             ) -> Dict[str, Any]:

        role = candidate_context.get("member", {}).get("jobRole", "Software Engineer")
        name = candidate_context.get("member", {}).get("name", "Candidate")
        covered_days = set(interview_state.get("curriculumDaysCovered", []))
        questions_asked = interview_state.get("questionsAsked", 0)

        # Handle follow-up request
        if force_follow_up:
            last_topic = interview_state.get("currentTopic", "your previous answer")
            difficulty = interview_state.get("currentDifficulty") or "foundation"
            reason = "Could you elaborate further on your technical implementation?"
            if latest_answer_evaluation and latest_answer_evaluation.get("follow_up_reason"):
                reason = latest_answer_evaluation.get("follow_up_reason")
            
            # Extract last answer for context
            last_candidate_msg = ""
            for entry in reversed(conversation_history):
                if entry.get("from") == "candidate":
                    last_candidate_msg = entry.get("text", "")
                    break

            if last_candidate_msg:
                question = f"That's a helpful point regarding {last_topic}. {reason}"
            else:
                question = f"Could you clarify your approach regarding {last_topic}? {reason}"

            return {
                "question": question,
                "curriculum_day": interview_state.get("currentCurriculumDay"),
                "topic": last_topic,
                "difficulty": difficulty,
                "question_type": "follow_up",
                "is_follow_up": True,
            }

        # Select next curriculum topic
        selected_day = None
        qtype = "concept"
        difficulty = "concept"

        for kind in ["skipped", "repeated", "completed", "other"]:
            candidates = curriculum_context.get(kind, [])
            for day in candidates:
                if not day:
                    continue
                dnum = day.get("day")
                if dnum in covered_days:
                    continue
                selected_day = day
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
                break
            if selected_day:
                break

        if not selected_day and curriculum_context.get("other"):
            selected_day = curriculum_context.get("other")[0]

        if selected_day:
            dnum = selected_day.get("day")
            is_first = (questions_asked == 0)
            question = self._generate_question_prompt(candidate_context, selected_day, difficulty, is_first)
            return {
                "question": question,
                "curriculum_day": dnum,
                "topic": selected_day.get("title"),
                "difficulty": difficulty,
                "question_type": qtype,
                "is_follow_up": False,
            }

        return {
            "question": f"Reflecting on your experience as a {role}, what is the most complex technical challenge or system trade-off you solved, and what lessons did you take away?",
            "curriculum_day": None,
            "topic": "System Design & Capstone",
            "difficulty": "application",
            "question_type": "open",
            "is_follow_up": False,
        }

