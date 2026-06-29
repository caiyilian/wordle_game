"""add_max_guesses_started_finished_at

Revision ID: bf1fb43fed00
Revises: 0002_room_members
Create Date: 2026-06-30 02:22:26.730772
"""

from alembic import op
import sqlalchemy as sa



revision = 'bf1fb43fed00'
down_revision = '0002_room_members'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('rooms', sa.Column('max_guesses', sa.Integer(), nullable=False, server_default='6'))
    op.add_column('rooms', sa.Column('started_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('rooms', sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('rooms', 'finished_at')
    op.drop_column('rooms', 'started_at')
    op.drop_column('rooms', 'max_guesses')
