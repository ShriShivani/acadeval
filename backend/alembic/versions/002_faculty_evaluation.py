"""Add faculty_evaluations table (AcadEval+ Module 7 ground truth)

Revision ID: 002
Revises: 001
Create Date: 2025-02-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "faculty_evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("evaluator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("faculty_score", sa.Float(), nullable=False),
        sa.Column("system_score", sa.Float(), nullable=False),
        sa.Column("score_delta", sa.Float(), nullable=False, server_default="0"),
        sa.Column("override_reason", sa.Text(), nullable=True),
        sa.Column("is_confirmed", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_faculty_evaluations_project_id", "faculty_evaluations", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_faculty_evaluations_project_id", table_name="faculty_evaluations")
    op.drop_table("faculty_evaluations")
