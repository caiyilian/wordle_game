from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(6), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="waiting")
    max_players: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    games: Mapped[list["GameRecord"]] = relationship(back_populates="room")


class GameRecord(Base):
    __tablename__ = "game_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    room_id: Mapped[str] = mapped_column(String(36), ForeignKey("rooms.id"), nullable=False, index=True)
    word_bank: Mapped[str] = mapped_column(String(20), nullable=False)
    answer_word: Mapped[str] = mapped_column(String(20), nullable=False)
    meaning: Mapped[str] = mapped_column(Text, nullable=False)
    word_length: Mapped[int] = mapped_column(Integer, nullable=False)
    max_guesses: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="playing")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    room: Mapped[Room] = relationship(back_populates="games")
    guesses: Mapped[list["PlayerGuess"]] = relationship(back_populates="game")


class PlayerGuess(Base):
    __tablename__ = "player_guesses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id: Mapped[str] = mapped_column(String(36), ForeignKey("game_records.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    guess_word: Mapped[str] = mapped_column(String(20), nullable=False)
    colors: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    guess_number: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    game: Mapped[GameRecord] = relationship(back_populates="guesses")
    user: Mapped["User"] = relationship(back_populates="guesses")
