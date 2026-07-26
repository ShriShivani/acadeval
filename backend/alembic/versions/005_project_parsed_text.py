"""Module 1 — store parsed abstract/full text on projects"""

from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("projects", sa.Column("abstract", sa.Text(), nullable=True))
    op.add_column("projects", sa.Column("parsed_text", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("projects", "parsed_text")
    op.drop_column("projects", "abstract")
