from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.services.graph_db import graph_service
from app.routers import (
    auth, projects, reports, reviews,
    appeals, rubrics, viva,
    leaderboard, dashboard, users,
    acadeval_plus
)

app = FastAPI(
    title="AcadEval API",
    description="AI-based Academic Project Evaluation Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static uploads ────────────────────────────────────────────────────────────
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ── Routers ───────────────────────────────────────────────────────────────────
API_PREFIX = "/api"

app.include_router(auth.router,          prefix=API_PREFIX)
app.include_router(projects.router,      prefix=API_PREFIX)
app.include_router(reports.router,       prefix=API_PREFIX)
app.include_router(reviews.router,       prefix=API_PREFIX)
app.include_router(appeals.router,       prefix=API_PREFIX)
app.include_router(rubrics.router,       prefix=API_PREFIX)
app.include_router(viva.router,          prefix=API_PREFIX)
app.include_router(leaderboard.router,   prefix=API_PREFIX)
app.include_router(dashboard.router,     prefix=API_PREFIX)
app.include_router(users.router,         prefix=API_PREFIX)
app.include_router(acadeval_plus.router, prefix=API_PREFIX)


@app.on_event("startup")
def on_startup():
    graph_service.ensure_constraints()


@app.on_event("shutdown")
def on_shutdown():
    graph_service.close()


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
