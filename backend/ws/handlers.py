from __future__ import annotations

from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.security import decode_access_token
from core.wordle import evaluate_guess
from core.word_loader import get_random_word
from database import AsyncSessionLocal
from ws.game_state import get_game_session, get_room_state, set_game_finished
from ws.manager import manager

router = APIRouter(tags=["websocket"])


def _make_event(event_type: str, **kwargs: Any) -> dict[str, Any]:
    event: dict[str, Any] = {"type": event_type}
    event.update(kwargs)
    return event


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: str,
) -> None:
    user_id = decode_access_token(token)
    if user_id is None:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await websocket.accept()
    await manager.connect(room_id, user_id, websocket)

    await manager.broadcast(
        room_id,
        _make_event("player_joined", user_id=user_id),
        exclude_user_id=user_id,
    )

    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            if event_type == "ping":
                await websocket.send_json(_make_event("pong"))

            elif event_type == "start_game":
                await _handle_start_game(room_id, user_id, websocket, data)

            elif event_type == "guess":
                await _handle_guess(room_id, user_id, websocket, data)

            elif event_type == "chat":
                message = data.get("message", "")
                if message:
                    await manager.broadcast(
                        room_id,
                        _make_event("chat", user_id=user_id, message=message),
                    )

            elif event_type == "leave":
                break

    except Exception:
        pass
    finally:
        await manager.disconnect(room_id, user_id)
        await manager.broadcast(
            room_id,
            _make_event("player_left", user_id=user_id),
        )


async def _handle_start_game(
    room_id: str,
    user_id: str,
    ws: WebSocket,
    data: dict[str, Any],
) -> None:
    room_state = get_room_state(room_id)
    session = AsyncSessionLocal()
    try:
        from sqlalchemy import select, update, func
        from models import Room

        result = await session.execute(select(Room).where(Room.id == room_id))
        room = result.scalar_one_or_none()

        if not room:
            await ws.send_json(_make_event("error", message="Room not found"))
            return

        if room.status != "waiting":
            await ws.send_json(_make_event("error", message="Game already started or finished"))
            return

        word_bank = room.word_bank or "CET4"
        word_length = room.word_length or 5
        max_guesses = room.max_guesses or 6

        answer_word, meaning = get_random_word(word_bank, word_length)
        room_state.start_game(word_bank, word_length, max_guesses, answer_word, meaning)

        room.status = "playing"
        await session.execute(
            update(Room)
            .where(Room.id == room_id)
            .values(status="playing", started_at=func.now())
        )
        await session.commit()

        await manager.broadcast(
            room_id,
            _make_event(
                "game_start",
                word_length=word_length,
                max_guesses=max_guesses,
                word_bank=word_bank,
            ),
        )
    finally:
        await session.close()


async def _handle_guess(
    room_id: str,
    user_id: str,
    ws: WebSocket,
    data: dict[str, Any],
) -> None:
    guess_word = data.get("word", "").strip().lower()

    if not guess_word:
        await ws.send_json(_make_event("error", message="No word provided"))
        return

    game_session = get_game_session(room_id)
    if not game_session or game_session.status != "playing":
        await ws.send_json(_make_event("error", message="No active game"))
        return

    if len(guess_word) != game_session.word_length:
        await ws.send_json(_make_event("error", message=f"Word must be {game_session.word_length} letters"))
        return

    colors = evaluate_guess(game_session.answer_word, guess_word)
    game_session.add_guess(user_id, guess_word, colors)

    await manager.broadcast(
        room_id,
        _make_event(
            "guess_result",
            user_id=user_id,
            word=guess_word,
            colors=colors,
            guess_number=game_session.current_turn,
        ),
    )

    won = all(c == "green" for c in colors)
    max_reached = game_session.current_turn >= game_session.max_guesses

    if won or max_reached:
        winner_id = user_id if won else None
        set_game_finished(room_id, winner_id)

        await manager.broadcast(
            room_id,
            _make_event(
                "game_over",
                status="win" if won else "loss",
                answer=game_session.answer_word,
                meaning=game_session.meaning,
                winner_id=winner_id,
                guesses=game_session.guess_history,
            ),
        )

        session = AsyncSessionLocal()
        try:
            from sqlalchemy import update, func
            from models import Room
            await session.execute(
                update(Room)
                .where(Room.id == room_id)
                .values(status="finished", finished_at=func.now())
            )
            await session.commit()
        finally:
            await session.close()
