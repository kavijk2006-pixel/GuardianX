# 🤖 GuardianX — The AI Technical Interviewer

> *“Build the interviewer, not the interview.”*

GuardianX is an AI Technical Interviewer platform that generates persona-driven, role-aware technical interview questions, adaptive follow-ups, and comprehensive candidate debriefs tailored to candidate backgrounds and resumes.

## 🌐 Live Web Application

- 🚀🚀 Global Public Web App (HTTPS)	https://kavijk2006-pixel.github.io/GuardianX/	Live globally on any mobile phone (iPhone/Android), tablet, or desktop over cellular data or Wi-Fi.
- 
⚡ Local Dev Web Server	http://127.0.0.1:3000/GuardianX_Web_App.html	Active local server running on port 3000.

🐙 GitHub Repository	https://github.com/kavijk2006-pixel/GuardianX	Fully synchronized main branch with complete source code & documentation.
## ✨ Key Features

1. **📄 Resume Upload & Candidate Selection**
   - Select pre-existing candidate profiles or upload custom candidate resumes.
   - Candidate information includes name, target role, years of experience, skills, and resume/bio context.

2. **🤖 Persona-Driven AI Interviewer**
   - Generates role-aware technical questions based on candidate context.
   - Evaluates answers and adapts follow-up questions.
   - Progresses across curriculum topics while avoiding repetitive follow-ups.

3. **💬 Mobile & Desktop Glassmorphic UI**
   - Modern dark-mode glassmorphism design.
   - Responsive layout for mobile, tablet, and desktop.
   - Interactive interview conversation experience.

4. **📊 Score & Assessment Dashboard**
   - Final interview summary.
   - Demonstrated strengths and knowledge gaps.
   - Actionable next steps for improvement.

## 🛠️ Tech Stack

- **Frontend:** React, Vite, HTML5, CSS
- **Backend:** Python, FastAPI, Uvicorn, Pydantic
- **Testing:** Pytest, HTTPX
- **LLM Integration:** Google Gemini SDK / OpenAI SDK support through the provider abstraction
- **Deployment:** GitHub Pages for the frontend; FastAPI backend can be deployed separately.

## 🏗️ Architecture

```text
                    GuardianX
                        │
              ┌─────────▼─────────┐
              │ React + Vite       │
              │ Frontend           │
              └─────────┬─────────┘
                        │
                 POST /api/interview
                        │
              ┌─────────▼─────────┐
              │ FastAPI Backend    │
              ├────────────────────┤
              │ Candidate Service  │
              │ Curriculum Service │
              │ Session Service    │
              │ Interviewer        │
              │ Evaluator          │
              │ Feedback           │
              │ LLM Provider       │
              └────────────────────┘
```

## 📁 Backend Structure

```text
backend/
├── main.py
├── models/
│   └── schemas.py
├── agents/
│   ├── interviewer.py
│   ├── evaluator.py
│   └── feedback.py
├── services/
│   ├── candidate_service.py
│   ├── curriculum_service.py
│   ├── session_service.py
│   └── interview_controller.py
└── llm/
    └── provider.py

tests/
├── test_candidates.py
├── test_curriculum.py
├── test_session_service.py
├── test_interview_controller.py
└── test_api.py
```

## 🚀 Running Locally

### Backend

```bash
python -m pip install fastapi uvicorn pytest httpx requests
python -m uvicorn backend.main:app --reload --port 8000
```

The FastAPI API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Run Tests

```bash
python -m pytest -q
```

## 🔄 Interview Flow

```text
Candidate Selection
        ↓
Start Interview
        ↓
Generate Question
        ↓
Candidate Answer
        ↓
Evaluate Answer
        ↓
Follow-up or Next Topic
        ↓
Minimum 8 Questions + 4 Curriculum Days
        ↓
Final Feedback
```

The backend enforces a minimum of **8 questions** and **4 distinct curriculum days** before completing an interview. Follow-ups are limited per curriculum day so the interview continues to progress instead of becoming stuck on one topic.

## 🧪 Continuous Integration

GitHub Actions runs the automated test suite using Python 3.11 and `pytest` on pushes and pull requests.

A successful workflow is indicated by the green check on the corresponding GitHub commit.

## 📋 Final Feedback Format

```json
{
  "reply": "Interview completed.",
  "done": true,
  "feedback": {
    "summary": "...",
    "strengths": ["..."],
    "gaps": ["..."],
    "next": ["..."]
  }
}
```

## 📌 Project Status

- ✅ FastAPI backend implemented
- ✅ Candidate and curriculum services implemented
- ✅ Session management implemented
- ✅ Interviewer, evaluator, and feedback components implemented
- ✅ Deterministic test provider available
- ✅ Automated API and service tests added
- ✅ GitHub Actions CI configured
- ✅ Frontend published through GitHub Pages

---

**GuardianX — Build the interviewer, not the interview.**
