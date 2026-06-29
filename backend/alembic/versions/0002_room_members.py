"""room members

Revision ID: 0002_room_members
Revises: 0001_initial_schema
Create Date: 2026-06-29 00:00:01
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_room_members"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("rooms", sa.Column("word_bank", sa.String(length=20), server_default="CET4", nullable=False))
    op.add_column("rooms", sa.Column("word_length", sa.Integer(), server_default="5", nullable=False))
    op.create_table(
        "room_members",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("room_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("room_id", "user_id", name="uq_room_members_room_user"),
    )
    op.create_index(op.f("ix_room_members_room_id"), "room_members", ["room_id"], unique=False)
    op.create_index(op.f("ix_room_members_user_id"), "room_members", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_room_members_user_id"), table_name="room_members")
    op.drop_index(op.f("ix_room_members_room_id"), table_name="room_members")
    op.drop_table("room_members")
    op.drop_column("rooms", "word_length")
    op.drop_column("rooms", "word_bank")
