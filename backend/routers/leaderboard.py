from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("", response_model=List[Dict[str, Any]])
async def get_leaderboard(
    session: AsyncSession = Depends(get_session),
    type: str = Query(default="wins", pattern="^(wins|win_rate|streak|total_games)$"),
    word_bank: str = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> List[Dict[str, Any]]:
    from models import User
    
    if type == "wins":
        stmt = select(User).order_by(User.wins.desc()).limit(limit)
    elif type == "win_rate":
        stmt = (
            select(User, (User.wins * 100.0 / func.nullif(User.total_games, 0)).label("rate"))
            .where(User.total_games > 0)
            .order_by(func.round((User.wins * 100.0 / func.nullif(User.total_games, 0)), 1).desc())
            .limit(limit)
        )
    elif type == "streak":
        stmt = select(User).order_by(User.max_streak.desc()).limit(limit)
    elif type == "total_games":
        stmt = select(User).order_by(User.total_games.desc()).limit(limit)
    else:
        stmt = select(User).order_by(User.wins.desc()).limit(limit)
    
    result = await session.execute(stmt)
    users = result.scalars().all()
    
    return [
        {
            "rank": i + 1,
            "user_id": u.id,
            "nickname": u.nickname,
            "total_games": u.total_games,
            "wins": u.wins,
            "current_streak": u.current_streak,
            "max_streak": u.max_streak,
            "win_rate": round(u.wins / max(u.total_games, 1) * 100, 1),
        }
        for i, u in enumerate(users)
    ]
