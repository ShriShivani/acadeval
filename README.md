# AcadEval — Monorepo

AI-powered academic project evaluation platform for engineering colleges.

## Structure

```
acadeval/
├── backend/     ← FastAPI backend (Python 3.11)
└── src/         ← React frontend (Vite + TypeScript)
```

## Quick Start

**Terminal 1 — Backend:**
```powershell
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```powershell
npm run dev
```

- Frontend → http://localhost:5173
- API docs  → http://localhost:8000/docs
