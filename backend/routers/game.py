from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import GameRecord, PlayerGuess

router = APIRouter(prefix="/api", tags=["games"])


@router.get("/games/{game_id}", response_model=dict)
async def get_game(
    game_id: str,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    result = await session.execute(select(GameRecord).where(GameRecord.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    guesses_result = await session.execute(
        select(PlayerGuess)
        .where(PlayerGuess.game_id == game_id)
        .order_by(PlayerGuess.guess_number)
    )
    guesses = guesses_result.all()

    return {
        "id": game.id,
        "room_id": game.room_id,
        "word_bank": game.word_bank,
        "answer_word": game.answer_word,
        "meaning": game.meaning,
        "word_length": game.word_length,
        "max_guesses": game.max_guesses,
        "status": game.status,
        "created_at": game.created_at.isoformat() if game.created_at else None,
        "finished_at": game.finished_at.isoformat() if game.finished_at else None,
        "guesses": [
            {
                "user_id": g.user_id,
                "word": g.guess_word,
                "colors": g.colors,
                "number": g.guess_number,
                "created_at": g.created_at.isoformat() if g.created_at else None,
            }
            for g in guesses
        ],
    }


@router.get("/games/{game_id}/history", response_model=dict)
async def get_game_history(
    game_id: str,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    return await get_game(game_id, session)
