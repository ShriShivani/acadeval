acadeval/                          ← monorepo root (git root)
│
├── backend/                       ← FastAPI backend (Python)
│   ├── .env                       ← secrets (git-ignored)
│   ├── .env.example               ← template to copy
│   ├── .gitignore                 ← backend-specific ignores
│   ├── docker-compose.yml         ← Postgres + Redis + API + Worker
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   │
│   ├── app/
│   │   ├── main.py                ← FastAPI app, CORS, mounts routers
│   │   ├── config.py              ← pydantic-settings from .env
│   │   ├── database.py            ← SQLAlchemy engine + get_db
│   │   ├── dependencies.py        ← get_current_user, require_role, typed aliases
│   │   ├── worker.py              ← Celery app factory
│   │   │
│   │   ├── models/                ← SQLAlchemy ORM (11 tables)
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── evaluation.py
│   │   │   ├── appeal.py
│   │   │   ├── rubric.py
│   │   │   └── viva.py
│   │   │
│   │   ├── schemas/               ← Pydantic v2 request/response models
│   │   │   ├── auth.py
│   │   │   ├── project.py
│   │   │   ├── report.py
│   │   │   ├── appeal.py
│   │   │   ├── rubric.py
│   │   │   ├── viva.py
│   │   │   ├── user.py
│   │   │   └── dashboard.py
│   │   │
│   │   ├── routers/               ← One router per API domain
│   │   │   ├── auth.py            POST /api/auth/login
│   │   │   ├── projects.py        GET/POST /api/projects
│   │   │   ├── reports.py         GET /api/projects/{id}/report/public|internal
│   │   │   ├── reviews.py         PATCH scores, POST notes/publish
│   │   │   ├── appeals.py         GET/POST/PATCH /api/appeals
│   │   │   ├── rubrics.py         GET/POST/PATCH /api/rubrics
│   │   │   ├── viva.py            GET questions, POST answer
│   │   │   ├── leaderboard.py     GET /api/leaderboard
│   │   │   ├── dashboard.py       GET /api/dashboard/faculty|hod + benchmarks
│   │   │   └── users.py           GET/PATCH /api/users (HOD only)
│   │   │
│   │   └── utils/
│   │       ├── auth.py            JWT encode/decode, bcrypt hash/verify
│   │       └── files.py           save_upload_file, get_file_type
│   │
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial_schema.py   ← Full DB migration (11 tables)
│   │
│   ├── scripts/
│   │   └── seed.py                ← 5 users + 4 projects + evaluations
│   │
│   ├── uploads/                   ← File storage (git-ignored)
│   └── venv/                      ← Python venv (git-ignored, recreate locally)
│
├── src/                           ← React frontend (TypeScript)
│   ├── api/                       ← Axios client + endpoints + mock data
│   ├── auth/                      ← AuthContext + RoleGuard
│   ├── components/                ← Shared UI components
│   ├── layouts/                   ← Student / Faculty / HOD layouts
│   ├── pages/                     ← All page components
│   └── types/                     ← TypeScript type definitions
│
├── public/
├── index.html
├── .env                           ← VITE_API_BASE_URL + VITE_USE_MOCK
├── .gitignore                     ← Combined frontend + backend ignores
├── package.json
├── tailwind.config.js
├── vite.config.ts
└── tsconfig.json
