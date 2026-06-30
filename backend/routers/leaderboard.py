from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("", response_model=List[Dict[str, Any]])
async def get_leaderboard(
    session: AsyncSession = Depends(get_session),
    type: str = Query(default="wins", pattern="^(wins|win_rate|streak|total_games|avg_guesses)$"),
    word_bank: str = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> List[Dict[str, Any]]:
    from models import GameRecord, PlayerGuess, User

    # Base query — join with GameRecord if word_bank filter is active
    # For avg_guesses we need a different query path
    if type == "avg_guesses":
        # Subquery: count guesses per user per game
        guess_counts = (
            select(
                PlayerGuess.user_id,
                PlayerGuess.game_id,
                func.count(PlayerGuess.id).label("guess_count"),
            )
            .group_by(PlayerGuess.user_id, PlayerGuess.game_id)
            .subquery()
        )

        # Build avg_guesses query
        avg_query = (
            select(
                User,
                func.coalesce(func.avg(guess_counts.c.guess_count), 0).label("avg_g"),
            )
            .outerjoin(guess_counts, guess_counts.c.user_id == User.id)
        )

        # Apply word_bank filter if provided
        if word_bank:
            # Only count games with matching word_bank
            avg_query = (
                select(
                    User,
                    func.coalesce(func.avg(guess_counts.c.guess_count), 0).label("avg_g"),
                )
                .outerjoin(guess_counts, guess_counts.c.user_id == User.id)
                .outerjoin(
                    GameRecord,
                    GameRecord.id == guess_counts.c.game_id,
                )
                .where(
                    (GameRecord.word_bank == word_bank) | (GameRecord.id.is_(None))
                )
            )

        avg_query = (
            avg_query
            .group_by(User.id)
            .order_by(text("avg_g ASC"))
            .limit(limit)
        )

        result = await session.execute(avg_query)
        rows = result.all()
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
                "avg_guesses": round(float(avg_g), 2) if avg_g else 0,
            }
            for i, (u, avg_g) in enumerate(rows)
        ]

    # Standard sort types (wins, win_rate, streak, total_games)
    if type == "wins":
        base_stmt = select(User).order_by(User.wins.desc())
    elif type == "win_rate":
        base_stmt = (
            select(User)
            .where(User.total_games > 0)
            .order_by(func.round((User.wins * 100.0 / func.nullif(User.total_games, 0)), 1).desc())
        )
    elif type == "streak":
        base_stmt = select(User).order_by(User.max_streak.desc())
    elif type == "total_games":
        base_stmt = select(User).order_by(User.total_games.desc())
    else:
        base_stmt = select(User).order_by(User.wins.desc())

    # Apply word_bank filter — restrict to users who have played in that word bank
    if word_bank:
        user_ids_subq = (
            select(PlayerGuess.user_id)
            .join(GameRecord, GameRecord.id == PlayerGuess.game_id)
            .where(GameRecord.word_bank == word_bank)
            .distinct()
            .subquery()
        )
        base_stmt = base_stmt.where(User.id.in_(select(user_ids_subq.c.user_id)))

    base_stmt = base_stmt.limit(limit)
    result = await session.execute(base_stmt)
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
