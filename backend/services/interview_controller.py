from typing import Dict, Any, Optional
from backend.services.candidate_service import CandidateService
from backend.services.curriculum_service import CurriculumService
from backend.services.session_service import SessionService
from backend.agents.interviewer import Interviewer
from backend.agents.evaluator import Evaluator
from backend.agents.feedback import FeedbackGenerator
from backend.llm.provider import LLMProvider

MIN_QUESTIONS = 8
MIN_CURRICULUM_DAYS = 4


class InterviewController:
    def __init__(self, session_service: SessionService = None, curriculum_service: CurriculumService = None,
                 candidate_service: CandidateService = None, llm_provider: Optional[LLMProvider] = None):
        self.session_service = session_service or SessionService()
        self.curriculum_service = curriculum_service or CurriculumService()
        self.candidate_service = candidate_service or CandidateService()
        self.interviewer = Interviewer()
        self.evaluator = Evaluator()
        self.feedback_generator = FeedbackGenerator()
        self.llm = llm_provider or LLMProvider()

    def start_interview(self, session_id: str, candidate_obj: Dict[str, Any]) -> Dict[str, Any]:
        # Validate and canonicalize candidate
        candidate = self.candidate_service.validate_candidate_object(candidate_obj)
        # Build contexts
        candidate_context = self.candidate_service.build_candidate_context(candidate)
        curriculum_context = self.curriculum_service.get_relevant_topics(candidate_context)
        # Create session
        session = self.session_service.create_session(session_id, candidate)
        # Store contexts in session for later
        session_update = {
            "candidate_context": candidate_context,
            "curriculum_context": curriculum_context,
        }
        self.session_service.update_session(session_id, session_update)

        # Decide first question
        decision = self.interviewer.decide_next_question(candidate_context, curriculum_context, [], session)
        question = decision.get("question")
        # Update session with question
        convo = session.get("conversationHistory", [])
        convo.append({"from": "ai", "text": question, "curriculum_day": decision.get("curriculum_day"), "topic": decision.get("topic")})
        session_update = {
            "conversationHistory": convo,
            "questionsAsked": session.get("questionsAsked", 0) + 1,
            "currentTopic": decision.get("topic"),
            "currentDifficulty": decision.get("difficulty"),
            "questionTypesUsed": session.get("questionTypesUsed", []) + [decision.get("question_type")],
            "lastReply": question,
            # Track the current curriculum day to manage follow-up limits
            "currentCurriculumDay": decision.get("curriculum_day"),
            # follow_up_count tracks number of follow-ups used for the currentCurriculumDay
            "follow_up_count": 0,
        }
        # Update curriculumDaysCovered and topicsCovered
        days = session.get("curriculumDaysCovered", [])
        dnum = decision.get("curriculum_day")
        if dnum and dnum not in days:
            days = days + [dnum]
            session_update["curriculumDaysCovered"] = days
        topics = session.get("topicsCovered", [])
        t = decision.get("topic")
        if t and t not in topics:
            topics = topics + [t]
            session_update["topicsCovered"] = topics

        self.session_service.update_session(session_id, session_update)

        return self.session_service.get_session(session_id)

    def handle_turn(self, session_id: str, message: str) -> Dict[str, Any]:
        # Retrieve session
        session = self.session_service.get_session(session_id)
        if session.get("interviewCompleted"):
            # Return final feedback if already completed
            feedback = self.feedback_generator.generate(session)
            return {"reply": "Interview completed.", "done": True, "feedback": feedback}

        # Record candidate answer
        convo = session.get("conversationHistory", [])
        convo.append({"from": "candidate", "text": message})

        # Evaluate the latest answer against the last AI question
        last_ai = None
        for entry in reversed(convo):
            if entry.get("from") == "ai":
                last_ai = entry
                break
        curriculum_day_obj = None
        if last_ai and last_ai.get("curriculum_day"):
            curriculum_day_obj = self.curriculum_service.get_day(last_ai.get("curriculum_day"))

        evaluation = self.evaluator.evaluate(last_ai or {}, message, curriculum_day_obj)

        # Store evaluation
        evals = session.get("answerEvaluations", [])
        evals.append(evaluation)

        # Update strengths and gaps
        strengths = session.get("strengths", [])
        gaps = session.get("gaps", [])
        for s in evaluation.get("strengths", []):
            if s not in strengths:
                strengths.append(s)
        for g in evaluation.get("gaps", []):
            if g not in gaps:
                gaps.append(g)

        # Decide next question
        candidate_context = session.get("candidate_context") or self.candidate_service.build_candidate_context(session.get("candidate"))
        curriculum_context = session.get("curriculum_context") or self.curriculum_service.get_relevant_topics(candidate_context)

        # If evaluator requests follow-up, allow at most one follow-up for the current curriculum day
        follow_up_needed = evaluation.get("follow_up_needed", False)
        follow_up_count = session.get("follow_up_count", 0)
        decision = None
        if follow_up_needed and follow_up_count == 0:
            # Allow one follow-up on the current topic
            decision = self.interviewer.decide_next_question(candidate_context, curriculum_context, convo, session, latest_answer_evaluation=evaluation, force_follow_up=True)
        else:
            # Either no follow-up needed, or we've already done one follow-up -> force progression
            decision = self.interviewer.decide_next_question(candidate_context, curriculum_context, convo, session, latest_answer_evaluation=evaluation, force_follow_up=False)

        # If no decision or no question, finish with feedback if coverage satisfied
        next_question = decision.get("question") if decision else None

        # Update session state with convo, evals, strengths, gaps
        session_updates = {
            "conversationHistory": convo,
            "answerEvaluations": evals,
            "strengths": strengths,
            "gaps": gaps,
            "lastReply": next_question,
        }

        # If next question exists, append and increment
        if next_question:
            # append AI question
            convo.append({"from": "ai", "text": next_question, "curriculum_day": decision.get("curriculum_day"), "topic": decision.get("topic")})
            session_updates["conversationHistory"] = convo
            session_updates["questionsAsked"] = session.get("questionsAsked", 0) + 1
            session_updates["currentTopic"] = decision.get("topic")
            session_updates["currentDifficulty"] = decision.get("difficulty")
            qtypes = session.get("questionTypesUsed", [])
            qtypes.append(decision.get("question_type"))
            session_updates["questionTypesUsed"] = qtypes

            # curriculum days/topics
            days = session.get("curriculumDaysCovered", [])
            dnum = decision.get("curriculum_day")
            # If we moved to a different curriculum day, reset follow_up_count
            prev_day = session.get("currentCurriculumDay")
            if dnum and dnum not in days:
                days = days + [dnum]
                session_updates["curriculumDaysCovered"] = days
            topics = session.get("topicsCovered", [])
            t = decision.get("topic")
            if t and t not in topics:
                topics = topics + [t]
                session_updates["topicsCovered"] = topics

            # Update currentCurriculumDay and manage follow_up_count
            if dnum != prev_day:
                # moved to a new day -> reset follow-up counter
                session_updates["currentCurriculumDay"] = dnum
                session_updates["follow_up_count"] = 0
            else:
                # same day: if this question was a follow-up, increment the counter
                if follow_up_needed and session.get("follow_up_count", 0) == 0 and decision.get("is_follow_up", False):
                    session_updates["follow_up_count"] = 1

        # Apply updates
        self.session_service.update_session(session_id, session_updates)

        # Check completion criteria
        s = self.session_service.get_session(session_id)
        questions_asked = s.get("questionsAsked", 0)
        curriculum_days = [d for d in s.get("curriculumDaysCovered", []) if d is not None]

        if questions_asked >= MIN_QUESTIONS and len(set(curriculum_days)) >= MIN_CURRICULUM_DAYS and not evaluation.get("follow_up_needed", False):
            # Complete interview
            feedback = self.feedback_generator.generate(s)
            self.session_service.update_session(session_id, {"interviewCompleted": True})
            return {"reply": "Interview completed.", "done": True, "feedback": feedback}

        # Otherwise return the next question
        return {"reply": next_question or "Thank you. I have no further questions.", "done": False}
