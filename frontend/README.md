# GuardianX Frontend

This is a minimal React (Vite) frontend that talks to the GuardianX backend API at /api/interview.

Features:
- Start an interview using a sessionId and a candidate object (Load CAND-004 if backend serves candidates.json)
- Send candidate messages and receive AI replies
- Display final feedback when interview completes

Local development
1. Start the backend (default):
   uvicorn backend.main:app --reload --port 8000

2. Start the frontend:
   cd frontend
   npm install
   npm run dev

The Vite dev server proxies /api requests to http://localhost:8000 (see vite.config.js). Ensure the backend is running before using the frontend.

Production
- Build the frontend with `npm run build` and serve the `dist` directory with any static server.

Notes
- The frontend uses the /api/interview contract implemented in backend/main.py. The backend stores sessions in memory; this frontend keeps a local transcript for display.
