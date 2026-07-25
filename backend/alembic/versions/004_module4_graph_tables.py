"""Module 4 - Relational Graph Storage (graph_nodes & graph_edges)

Revision ID: 004
Revises: 003
Create Date: 2026-07-25 00:00:00.000000

Changes:
  - Add `graph_nodes` table with UNIQUE(node_type, name) constraint
  - Add `graph_edges` table with foreign keys to graph_nodes(id)
"""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── graph_nodes table ────────────────────────────────────────────────────────
    op.create_table(
        "graph_nodes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "node_type",
            sa.String(50),
            nullable=False,
            comment="Project | Domain | Subdomain | Algorithm | Technology | Framework | Library | Dataset | Application | Hardware | Metric",
        ),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("node_type", "name", name="uq_graph_nodes_type_name"),
    )
    op.create_index("ix_graph_nodes_type", "graph_nodes", ["node_type"])
    op.create_index("ix_graph_nodes_name", "graph_nodes", ["name"])

    # ── graph_edges table ────────────────────────────────────────────────────────
    op.create_table(
        "graph_edges",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "from_node",
            sa.Integer(),
            sa.ForeignKey("graph_nodes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "to_node",
            sa.Integer(),
            sa.ForeignKey("graph_nodes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "relationship",
            sa.String(50),
            nullable=False,
            comment="HAS_DOMAIN | HAS_SUBDOMAIN | USES_ALGORITHM | USES_TECHNOLOGY | USES_FRAMEWORK | USES_LIBRARY | USES_DATASET | TARGETS_APPLICATION | RUNS_ON | EVALUATED_BY | CO_OCCURS",
        ),
        sa.Column(
            "confidence",
            sa.Numeric(precision=5, scale=4),
            nullable=False,
            server_default="1.0000",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_graph_edges_from", "graph_edges", ["from_node"])
    op.create_index("ix_graph_edges_to", "graph_edges", ["to_node"])
    op.create_index("ix_graph_edges_rel", "graph_edges", ["relationship"])


def downgrade() -> None:
    op.drop_index("ix_graph_edges_rel", table_name="graph_edges")
    op.drop_index("ix_graph_edges_to", table_name="graph_edges")
    op.drop_index("ix_graph_edges_from", table_name="graph_edges")
    op.drop_table("graph_edges")

    op.drop_index("ix_graph_nodes_name", table_name="graph_nodes")
    op.drop_index("ix_graph_nodes_type", table_name="graph_nodes")
    op.drop_table("graph_nodes")
