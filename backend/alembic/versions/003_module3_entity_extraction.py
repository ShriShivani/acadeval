"""Module 3 - Entity extraction storage

Revision ID: 003
Revises: 002
Create Date: 2026-07-25 00:00:00.000000

Changes:
  - Add `extracted_entities` JSONB column to `projects` table
    (stores Module 3's structured entity output so it is never re-extracted on
     every report request; nullable so existing rows are unaffected)
  - Add `feature_knowledge_base` table for the AcadEval_FeatureKnowledgeBase
    (mirrors the CSV/JSON file in PostgreSQL so future modules can query it
     with SQL and the faculty pending-review workflow can approve entries directly)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── projects: cache Module 3 output ──────────────────────────────────────────
    op.add_column(
        "projects",
        sa.Column(
            "extracted_entities",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment=(
                "Cached output of Module 3 entity extraction. "
                "Shape: {algorithms[], technologies[], frameworks[], libraries[], "
                "datasets[], applications[], hardware[], metrics[], unmatched_spans[]}"
            ),
        ),
    )

    # ── feature_knowledge_base table ─────────────────────────────────────────────
    op.create_table(
        "feature_knowledge_base",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False, unique=True),
        sa.Column(
            "category",
            sa.String(50),
            nullable=False,
            comment="algorithm | technology | framework | library | dataset | application | hardware | metric",
        ),
        sa.Column(
            "aliases",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="[]",
            comment="List of alternative names / abbreviations",
        ),
        sa.Column(
            "first_seen_year",
            sa.Integer(),
            nullable=True,
            comment="Year the term first appeared in the literature",
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "is_approved",
            sa.Boolean(),
            nullable=False,
            server_default="true",
            comment="False = pending faculty review (came from pending_review.json)",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_fkb_name", "feature_knowledge_base", ["name"])
    op.create_index("ix_fkb_category", "feature_knowledge_base", ["category"])
    op.create_index("ix_fkb_approved", "feature_knowledge_base", ["is_approved"])


def downgrade() -> None:
    op.drop_index("ix_fkb_approved", table_name="feature_knowledge_base")
    op.drop_index("ix_fkb_category", table_name="feature_knowledge_base")
    op.drop_index("ix_fkb_name", table_name="feature_knowledge_base")
    op.drop_table("feature_knowledge_base")
    op.drop_column("projects", "extracted_entities")
