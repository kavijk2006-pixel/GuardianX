from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class StartInterviewRequest(BaseModel):
    sessionId: str
    candidate: Dict[str, Any]


class TurnRequest(BaseModel):
    sessionId: str
    message: str


class Feedback(BaseModel):
    summary: str
    strengths: List[str]
    gaps: List[str]
    next: List[str]


class InterviewResponse(BaseModel):
    reply: str
    done: bool
    feedback: Optional[Feedback] = None


class Member(BaseModel):
    id: str
    name: str
    jobRole: Optional[str]
    yearsExperience: Optional[int]
    education: Optional[str]
    status: Optional[str]


class Mission(BaseModel):
    day: int
    title: str
    passed: Optional[bool] = None
    skipped: Optional[bool] = None
    attempts: Optional[int] = None


class Candidate(BaseModel):
    member: Member
    missions: List[Mission]
    signals: Dict[str, Any]


class AnswerEvaluation(BaseModel):
    correctness: int
    understanding: int
    practical: int
    depth: int
    clarity: int
    problem_solving: int
    strengths: List[str]
    gaps: List[str]
    follow_up_needed: bool
    follow_up_reason: Optional[str]


class InterviewState(BaseModel):
    sessionId: str
    candidate_id: str
    questionsAsked: int = 0
    curriculumDaysCovered: List[int] = Field(default_factory=list)
    topicsCovered: List[str] = Field(default_factory=list)
    conversationHistory: List[Dict[str, Any]] = Field(default_factory=list)
    answerEvaluations: List[AnswerEvaluation] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    currentTopic: Optional[str] = None
    currentDifficulty: Optional[str] = None
    questionTypesUsed: List[str] = Field(default_factory=list)
    interviewCompleted: bool = False
