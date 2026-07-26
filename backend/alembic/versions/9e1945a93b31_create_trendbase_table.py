"""create_trendbase_table

Revision ID: 9e1945a93b31
Revises: 28ef79fbfcbc
Create Date: 2026-07-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9e1945a93b31'
down_revision = '28ef79fbfcbc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'acadeval_trendbase',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('topic', sa.String(length=255), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('paper_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('citation_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('topic', 'year', name='uq_trendbase_topic_year')
    )
    op.create_index('ix_acadeval_trendbase_topic', 'acadeval_trendbase', ['topic'])
    op.create_index('ix_acadeval_trendbase_year', 'acadeval_trendbase', ['year'])


def downgrade() -> None:
    op.drop_index('ix_acadeval_trendbase_year', table_name='acadeval_trendbase')
    op.drop_index('ix_acadeval_trendbase_topic', table_name='acadeval_trendbase')
    op.drop_table('acadeval_trendbase')
