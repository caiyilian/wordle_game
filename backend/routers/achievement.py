from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.achievements import get_all_achievements
from database import get_session
from models import User

router = APIRouter(prefix="/api/users", tags=["achievements"])


@router.get("/{user_id}/achievements", response_model=List[Dict[str, Any]])
async def get_user_achievements(
    user_id: str,
    session: AsyncSession = Depends(get_session),
) -> List[Dict[str, Any]]:
    """Get all achievements and their unlock status for a user."""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        return [
            {**a, "unlocked": False}
            for a in [
                {"id": "first_win", "name": "First Win", "desc": "Win your first game"},
                {"id": "perfect_guess", "name": "Perfect Guess", "desc": "Guess in one try"},
                {"id": "streak_5", "name": "On Fire", "desc": "Win 5 in a row"},
                {"id": "streak_10", "name": "Unstoppable", "desc": "Win 10 in a row"},
                {"id": "shooter", "name": "Sharpshooter", "desc": "3 wins within 3 guesses"},
                {"id": "veteran", "name": "Veteran", "desc": "Play 50 games"},
                {"id": "half_century", "name": "Half Century", "desc": "Play 100 games"},
            ]
        ]

    stats = {
        "total_games": user.total_games,
        "wins": user.wins,
        "current_streak": user.current_streak,
        "max_streak": user.max_streak,
        "guess_distribution": user.guess_distribution or {},
    }
    return get_all_achievements(stats)