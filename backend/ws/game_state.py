from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GameSession:
    """In-memory game session for a room."""
    room_id: str
    answer_word: str = ""
    meaning: str = ""
    word_bank: str = ""
    word_length: int = 5
    max_guesses: int = 6
    status: str = "waiting"
    guess_history: list = field(default_factory=list)
    winner_id: str | None = None
    current_turn: int = 0

    def add_guess(self, user_id: str, guess_word: str, colors: list[str]) -> None:
        self.guess_history.append({
            "user_id": user_id,
            "word": guess_word,
            "colors": colors,
            "number": len(self.guess_history) + 1,
        })
        self.current_turn += 1

    def finish(self, winner_id: str | None = None) -> None:
        self.status = "finished"
        self.winner_id = winner_id


@dataclass
class RoomState:
    """Tracks the game state for a room."""
    room_id: str
    game: GameSession | None = None
    game_started: bool = False

    def start_game(self, word_bank: str, word_length: int, max_guesses: int, answer_word: str, meaning: str) -> None:
        self.game = GameSession(
            room_id=self.room_id,
            answer_word=answer_word,
            meaning=meaning,
            word_bank=word_bank,
            word_length=word_length,
            max_guesses=max_guesses,
            status="playing",
        )
        self.game_started = True


# Global in-memory game state
_room_states: dict[str, RoomState] = {}


def get_room_state(room_id: str) -> RoomState:
    if room_id not in _room_states:
        _room_states[room_id] = RoomState(room_id=room_id)
    return _room_states[room_id]


def get_game_session(room_id: str) -> GameSession | None:
    state = _room_states.get(room_id)
    if state:
        return state.game
    return None


def set_game_finished(room_id: str, winner_id: str | None = None) -> None:
    state = _room_states.get(room_id)
    if state and state.game:
        state.game.finish(winner_id)


def clear_room_state(room_id: str) -> None:
    _room_states.pop(room_id, None)
