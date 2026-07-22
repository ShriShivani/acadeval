"""Initial full schema

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── ENUM types ──────────────────────────────────────────────────────────────
    userrole = postgresql.ENUM("student", "guide", "reviewer", "hod", name="userrole", create_type=False)
    userrole.create(op.get_bind(), checkfirst=True)

    submissiontype = postgresql.ENUM("document", "video", "abstract", name="submissiontype", create_type=False)
    submissiontype.create(op.get_bind(), checkfirst=True)

    pipelinestatus = postgresql.ENUM("uploaded", "ai_processing", "awaiting_review", "reviewed", name="pipelinestatus", create_type=False)
    pipelinestatus.create(op.get_bind(), checkfirst=True)

    appealstatus = postgresql.ENUM("pending", "under_review", "resolved", "rejected", name="appealstatus", create_type=False)
    appealstatus.create(op.get_bind(), checkfirst=True)

    # ── users ───────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("roll_no", sa.String(50), unique=True, nullable=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("student", "guide", "reviewer", "hod", name="userrole"), nullable=False),
        sa.Column("department", sa.String(100), nullable=False, server_default="CSE"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # ── projects ─────────────────────────────────────────────────────────────────
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("domain", sa.String(100), nullable=False),
        sa.Column("submission_type", sa.Enum("document", "video", "abstract", name="submissiontype"), nullable=False),
        sa.Column("github_url", sa.String(500), nullable=True),
        sa.Column("related_submission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=True),
        sa.Column("pipeline_status", sa.Enum("uploaded", "ai_processing", "awaiting_review", "reviewed", name="pipelinestatus"), nullable=False, server_default="uploaded"),
        sa.Column("assigned_guide_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("assigned_reviewer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("is_preliminary", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("submitted_on", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_projects_student_id", "projects", ["student_id"])

    # ── project_files ────────────────────────────────────────────────────────────
    op.create_table(
        "project_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("file_type", sa.String(50), nullable=False),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("storage_path", sa.String(1000), nullable=False),
        sa.Column("extracted_text_path", sa.String(1000), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_project_files_project_id", "project_files", ["project_id"])

    # ── evaluation_reports ───────────────────────────────────────────────────────
    op.create_table(
        "evaluation_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), unique=True, nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("grade", sa.String(5), nullable=False, server_default=""),
        sa.Column("novelty_score", sa.Float(), nullable=True),
        sa.Column("feasibility_score", sa.Float(), nullable=True),
        sa.Column("completeness_score", sa.Float(), nullable=True),
        sa.Column("technical_depth_score", sa.Float(), nullable=True),
        sa.Column("clarity_score", sa.Float(), nullable=True),
        sa.Column("similarity_risk_score", sa.Float(), nullable=True),
        sa.Column("publication_potential_score", sa.Float(), nullable=True),
        sa.Column("similarity_internal", sa.Float(), nullable=False, server_default="0"),
        sa.Column("similarity_external", sa.Float(), nullable=False, server_default="0"),
        sa.Column("is_duplicate", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("feasibility_rating", sa.String(20), nullable=False, server_default="Medium"),
        sa.Column("novelty_verdict", sa.String(30), nullable=False, server_default="Somewhat Novel"),
        sa.Column("missing_sections", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("writing_quality", postgresql.JSONB(), nullable=True),
        sa.Column("citations", postgresql.JSONB(), nullable=True),
        sa.Column("strengths", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("weaknesses", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("improvement_roadmap", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("badges", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("percentile_ranks", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("flagging_reasons", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("explainability_annotations", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── internal_notes ───────────────────────────────────────────────────────────
    op.create_table(
        "internal_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_internal_notes_project_id", "internal_notes", ["project_id"])

    # ── score_override_history ───────────────────────────────────────────────────
    op.create_table(
        "score_override_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("evaluation_reports.id"), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dimension", sa.String(50), nullable=False),
        sa.Column("old_value", sa.Float(), nullable=False),
        sa.Column("new_value", sa.Float(), nullable=False),
        sa.Column("changed_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("changed_by_name", sa.String(200), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── historical_scores ────────────────────────────────────────────────────────
    op.create_table(
        "historical_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("dimension", sa.String(50), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("semester", sa.String(20), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
    )

    # ── rubrics ──────────────────────────────────────────────────────────────────
    op.create_table(
        "rubrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("department", sa.String(100), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("criteria", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── appeals ──────────────────────────────────────────────────────────────────
    op.create_table(
        "appeals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("dimension", sa.String(50), nullable=False),
        sa.Column("original_score", sa.Float(), nullable=False),
        sa.Column("student_justification", sa.Text(), nullable=False),
        sa.Column("status", sa.Enum("pending", "under_review", "resolved", "rejected", name="appealstatus"), nullable=False, server_default="pending"),
        sa.Column("faculty_response", sa.Text(), nullable=True),
        sa.Column("resolved_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_appeals_project_id", "appeals", ["project_id"])

    # ── viva_sessions ────────────────────────────────────────────────────────────
    op.create_table(
        "viva_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("questions", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("answers", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("scores", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("is_complete", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("total_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_viva_sessions_project_id", "viva_sessions", ["project_id"])


def downgrade() -> None:
    op.drop_table("viva_sessions")
    op.drop_table("appeals")
    op.drop_table("rubrics")
    op.drop_table("historical_scores")
    op.drop_table("score_override_history")
    op.drop_table("internal_notes")
    op.drop_table("evaluation_reports")
    op.drop_table("project_files")
    op.drop_table("projects")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS appealstatus")
    op.execute("DROP TYPE IF EXISTS pipelinestatus")
    op.execute("DROP TYPE IF EXISTS submissiontype")
    op.execute("DROP TYPE IF EXISTS userrole")
