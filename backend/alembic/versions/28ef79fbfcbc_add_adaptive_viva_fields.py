"""add_adaptive_viva_fields

Revision ID: 28ef79fbfcbc
Revises: ae74d8961c6d
Create Date: 2026-07-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '28ef79fbfcbc'
down_revision = 'ae74d8961c6d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('viva_sessions', sa.Column('kcs', sa.Float(), nullable=True))
    op.add_column('viva_sessions', sa.Column('current_difficulty', sa.String(length=32), nullable=True))
    op.add_column('viva_sessions', sa.Column('difficulty_progression', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('viva_sessions', sa.Column('consecutive_correct', sa.Integer(), nullable=True))
    op.add_column('viva_sessions', sa.Column('consecutive_wrong', sa.Integer(), nullable=True))
    op.add_column('viva_sessions', sa.Column('report', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('viva_sessions', 'report')
    op.drop_column('viva_sessions', 'consecutive_wrong')
    op.drop_column('viva_sessions', 'consecutive_correct')
    op.drop_column('viva_sessions', 'difficulty_progression')
    op.drop_column('viva_sessions', 'current_difficulty')
    op.drop_column('viva_sessions', 'kcs')
