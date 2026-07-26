"""add_celery_task_id_to_projects

Revision ID: ae74d8961c6d
Revises: 004
Create Date: 2026-07-26

Module 11 — adds celery_task_id column to projects so the pipeline-status
endpoint can poll the Celery AsyncResult for live progress.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'ae74d8961c6d'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'projects',
        sa.Column('celery_task_id', sa.String(length=128), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('projects', 'celery_task_id')
