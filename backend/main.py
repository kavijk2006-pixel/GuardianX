from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from backend.services.session_service import SessionService
from backend.services.candidate_service import CandidateService
from backend.services.curriculum_service import CurriculumService
from backend.services.interview_controller import InterviewController

app = FastAPI(title="AI Interview Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = SessionService()
curriculum_service = CurriculumService()
candidate_service = CandidateService()
interview_controller = InterviewController(session_service, curriculum_service)


class StartRequest(BaseModel):
    sessionId: str
    candidate: dict


class TurnRequest(BaseModel):
    sessionId: str
    message: str


@app.post('/api/interview')
async def interview(payload: dict):
    # Determine whether this is start or turn based on payload keys
    if 'sessionId' not in payload:
        raise HTTPException(status_code=400, detail="Missing sessionId")

    session_id = payload['sessionId']

    # Start interview
    if 'candidate' in payload:
        candidate_obj = payload['candidate']
        try:
            candidate = candidate_service.validate_candidate_object(candidate_obj)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Create session
        session = interview_controller.start_interview(session_id, candidate)
        return {"reply": session['lastReply'], "done": False}

    # Conversation turn
    if 'message' in payload:
        message = payload['message']
        if not isinstance(message, str) or message.strip() == '':
            raise HTTPException(status_code=400, detail="Empty candidate message")
        try:
            result = interview_controller.handle_turn(session_id, message)
        except KeyError:
            raise HTTPException(status_code=404, detail="Unknown session")

        return result

    raise HTTPException(status_code=400, detail="Invalid request payload")
