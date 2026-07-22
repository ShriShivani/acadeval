"""
Seed script — creates one account per role + one sample reviewed project.
Run after migrations: python scripts/seed.py

Works both inside Docker:  docker-compose exec api python scripts/seed.py
And locally:               python scripts/seed.py  (with .env.local pointing to localhost:5432)
"""
import sys
import os
import uuid
from datetime import datetime, timezone

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.project import Project, PipelineStatus, SubmissionType
from app.models.evaluation import EvaluationReport, HistoricalScore
from app.utils.auth import hash_password

# ── Seed data ──────────────────────────────────────────────────────────────────

SEED_USERS = [
    {
        "name": "Priya Sharma",
        "roll_no": "CS2021001",
        "email": "priya@college.edu",
        "password": "demo123",
        "role": UserRole.student,
        "department": "CSE",
    },
    {
        "name": "Arjun Patel",
        "roll_no": "CS2021002",
        "email": "arjun@college.edu",
        "password": "demo123",
        "role": UserRole.student,
        "department": "CSE",
    },
    {
        "name": "Dr. Meera Krishnan",
        "roll_no": None,
        "email": "meera@college.edu",
        "password": "demo123",
        "role": UserRole.guide,
        "department": "CSE",
    },
    {
        "name": "Prof. Suresh Rajan",
        "roll_no": None,
        "email": "suresh@college.edu",
        "password": "demo123",
        "role": UserRole.reviewer,
        "department": "CSE",
    },
    {
        "name": "Dr. Anand Krishnamurthy",
        "roll_no": None,
        "email": "hod@college.edu",
        "password": "demo123",
        "role": UserRole.hod,
        "department": "CSE",
    },
]


def seed():
    db = SessionLocal()
    print("─── AcadEval Seed Script ───────────────────────────────────")

    # ── Create users ───────────────────────────────────────────────────────────
    created_users: dict[str, User] = {}
    for u_data in SEED_USERS:
        existing = db.query(User).filter(User.email == u_data["email"]).first()
        if existing:
            print(f"  [SKIP] User already exists: {u_data['email']}")
            created_users[u_data["email"]] = existing
            continue

        user = User(
            name=u_data["name"],
            roll_no=u_data["roll_no"],
            email=u_data["email"],
            password_hash=hash_password(u_data["password"]),
            role=u_data["role"],
            department=u_data["department"],
        )
        db.add(user)
        db.flush()
        created_users[u_data["email"]] = user
        print(f"  [OK]   Created {u_data['role'].value}: {u_data['email']}")

    db.commit()

    # ── Create sample projects ─────────────────────────────────────────────────
    student = created_users["priya@college.edu"]
    guide = created_users["meera@college.edu"]
    reviewer = created_users["suresh@college.edu"]

    def make_project(title: str, domain: str, sub_type: SubmissionType, status: PipelineStatus, score: float = 0) -> Project:
        existing = db.query(Project).filter(Project.title == title, Project.student_id == student.id).first()
        if existing:
            print(f"  [SKIP] Project already exists: {title[:40]}...")
            return existing

        project = Project(
            student_id=student.id,
            title=title,
            domain=domain,
            submission_type=sub_type,
            pipeline_status=status,
            assigned_guide_id=guide.id,
            assigned_reviewer_id=reviewer.id,
            is_preliminary=(status != PipelineStatus.reviewed),
        )
        db.add(project)
        db.flush()

        if score > 0:
            report = EvaluationReport(
                project_id=project.id,
                overall_score=score,
                grade="A+" if score >= 90 else "A" if score >= 80 else "B" if score >= 70 else "C",
                novelty_score=round(score * 0.9, 1),
                feasibility_score=round(score * 0.95, 1),
                completeness_score=None if sub_type == SubmissionType.abstract else round(score * 0.85, 1),
                technical_depth_score=round(score * 1.02, 1),
                clarity_score=round(score * 0.88, 1),
                similarity_risk_score=round(score * 0.75, 1),
                publication_potential_score=round(score * 0.80, 1),
                feasibility_rating="High" if score >= 80 else "Medium",
                novelty_verdict="Novel" if score >= 85 else "Somewhat Novel",
                strengths=[
                    "Strong technical implementation with clear system architecture",
                    "Well-documented dataset preparation and preprocessing pipeline",
                    "Comprehensive evaluation metrics with benchmark comparisons",
                    "Novel application of transformer models to the agricultural domain",
                ],
                weaknesses=[
                    "Literature review could be expanded with more recent papers (2023–2024)",
                    "Edge case handling for low-quality image inputs not addressed",
                    "Deployment scalability analysis is missing",
                ],
                missing_sections=[] if sub_type != SubmissionType.abstract else ["completeness", "citations"],
                improvement_roadmap=[
                    {"week": 1, "focus": "Literature Expansion", "actions": [
                        "Add 5 recent IEEE/ACM papers from 2023–2024",
                        "Update Related Work section with proper IEEE citations",
                        "Run citation validator tool to fix formatting",
                    ]},
                    {"week": 2, "focus": "Edge Case Hardening", "actions": [
                        "Add image quality validation module",
                        "Test with low-resolution and occluded crop images",
                        "Add confidence thresholding for ambiguous predictions",
                    ]},
                    {"week": 3, "focus": "Scalability Analysis", "actions": [
                        "Document deployment architecture for 1,000+ concurrent farms",
                        "Benchmark inference speed on Raspberry Pi 4",
                        "Add Docker deployment guide to the repository",
                    ]},
                    {"week": 4, "focus": "Publication Preparation", "actions": [
                        "Format paper to IEEE conference template",
                        "Identify target venue (e.g. ICASSP, IEEE IoT Journal)",
                        "Prepare supplementary materials and code repository",
                    ]},
                ],
                badges=["Novel Idea Award", "Publication Ready"] if score >= 85 else [],
                percentile_ranks={"novelty": 88, "feasibility": 82, "overall": 85},
                writing_quality={"readability": 72.4, "passiveVoiceCount": 8, "toneFlags": ["Avoid hedge words like 'might' in the conclusion"]},
                citations={"ieeeCompliancePercent": 78.0, "missingReferences": ["[5] Author et al. — incomplete year", "[12] URL reference — missing access date"]},
                published_at=datetime.now(timezone.utc) if status == PipelineStatus.reviewed else None,
            )
            db.add(report)

            # Seed historical scores for benchmarking
            for dim, val in [("novelty", report.novelty_score), ("feasibility", report.feasibility_score), ("overall", score)]:
                if val is not None:
                    db.add(HistoricalScore(project_id=project.id, dimension=dim, score=val, semester="Even", year=2025))

        db.commit()
        print(f"  [OK]   Created project: {title[:50]}... [{status.value}] score={score}")
        return project

    make_project("AI-Powered Crop Disease Detection Using Deep Learning", "AI/ML", SubmissionType.document, PipelineStatus.reviewed, 84.0)
    make_project("Smart Irrigation System with IoT Sensors", "IoT", SubmissionType.abstract, PipelineStatus.awaiting_review, 71.0)
    make_project("Blockchain-Based Academic Certificate Verification", "Web/App", SubmissionType.document, PipelineStatus.ai_processing, 0)

    # Seed Arjun's project
    arjun = created_users["arjun@college.edu"]
    existing = db.query(Project).filter(Project.student_id == arjun.id).first()
    if not existing:
        p = Project(
            student_id=arjun.id,
            title="Real-Time Hand Gesture Recognition using MediaPipe",
            domain="AI/ML",
            submission_type=SubmissionType.video,
            pipeline_status=PipelineStatus.reviewed,
            assigned_guide_id=guide.id,
            is_preliminary=False,
        )
        db.add(p)
        db.flush()
        r = EvaluationReport(
            project_id=p.id,
            overall_score=91.0,
            grade="A+",
            novelty_score=92, feasibility_score=90, completeness_score=88,
            technical_depth_score=94, clarity_score=89, similarity_risk_score=85,
            publication_potential_score=91,
            feasibility_rating="High",
            novelty_verdict="Novel",
            strengths=["Exceptional technical depth", "Very high novelty", "Publication-quality results"],
            weaknesses=["Abstract could be more concise"],
            improvement_roadmap=[{"week": 1, "focus": "Paper Submission", "actions": ["Submit to IEEE CVPR workshop"]}],
            badges=["Novel Idea Award", "Top Scorer", "Publication Ready"],
            percentile_ranks={"novelty": 96, "overall": 94},
            published_at=datetime.now(timezone.utc),
        )
        db.add(r)
        db.commit()
        print(f"  [OK]   Created project for Arjun: Real-Time Hand Gesture Recognition... [reviewed] score=91.0")

    print("\n─── Seed complete! ─────────────────────────────────────────")
    print("\nDemo credentials (all passwords: demo123):")
    print("  Student:  priya@college.edu  / arjun@college.edu")
    print("  Guide:    meera@college.edu")
    print("  Reviewer: suresh@college.edu")
    print("  HOD:      hod@college.edu")
    db.close()


if __name__ == "__main__":
    seed()
