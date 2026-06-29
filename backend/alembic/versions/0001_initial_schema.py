"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-29 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("nickname", sa.String(length=20), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("avatar_url", sa.String(length=255), nullable=True),
        sa.Column("total_games", sa.Integer(), nullable=False),
        sa.Column("wins", sa.Integer(), nullable=False),
        sa.Column("current_streak", sa.Integer(), nullable=False),
        sa.Column("max_streak", sa.Integer(), nullable=False),
        sa.Column("guess_distribution", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_nickname"), "users", ["nickname"], unique=True)

    op.create_table(
        "rooms",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=6), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("max_players", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rooms_code"), "rooms", ["code"], unique=True)

    op.create_table(
        "game_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("room_id", sa.String(length=36), nullable=False),
        sa.Column("word_bank", sa.String(length=20), nullable=False),
        sa.Column("answer_word", sa.String(length=20), nullable=False),
        sa.Column("meaning", sa.Text(), nullable=False),
        sa.Column("word_length", sa.Integer(), nullable=False),
        sa.Column("max_guesses", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_game_records_room_id"), "game_records", ["room_id"], unique=False)

    op.create_table(
        "player_guesses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("game_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("guess_word", sa.String(length=20), nullable=False),
        sa.Column("colors", sa.JSON(), nullable=False),
        sa.Column("guess_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["game_records.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_player_guesses_game_id"), "player_guesses", ["game_id"], unique=False)
    op.create_index(op.f("ix_player_guesses_user_id"), "player_guesses", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_player_guesses_user_id"), table_name="player_guesses")
    op.drop_index(op.f("ix_player_guesses_game_id"), table_name="player_guesses")
    op.drop_table("player_guesses")
    op.drop_index(op.f("ix_game_records_room_id"), table_name="game_records")
    op.drop_table("game_records")
    op.drop_index(op.f("ix_rooms_code"), table_name="rooms")
    op.drop_table("rooms")
    op.drop_index(op.f("ix_users_nickname"), table_name="users")
    op.drop_table("users")
