from __future__ import annotations

import hashlib
from datetime import date
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.word_loader import WORD_BANKS, get_available_word_lengths, get_random_word
from database import get_session

router = APIRouter(prefix="/api/daily", tags=["daily"])


def _get_daily_seed() -> str:
    """Get today date as seed string."""
    return date.today().isoformat()


def _select_daily_word(word_bank: str = "CET4", length: int = 5) -> tuple:
    """Select a deterministic word for today based on date seed."""
    seed = _get_daily_seed()
    # Use a deterministic hash to pick from available words
    words_by_length = WORD_BANKS.get(word_bank, {}).get(length, [])
    if not words_by_length:
        raise HTTPException(status_code=400, detail=f"No words for bank {word_bank} length {length}")
    
    hash_val = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    idx = hash_val % len(words_by_length)
    return words_by_length[idx]


@router.get("/word")
def get_daily_word(
    word_bank: str = Query(default="CET4"),
    length: int = Query(default=5, ge=3, le=10),
) -> Dict[str, Any]:
    """Get today daily challenge word info (without revealing the answer)."""
    words = WORD_BANKS.get(word_bank, {}).get(length, [])
    if not words:
        raise HTTPException(status_code=404, detail=f"No words available for {word_bank} length {length}")
    
    word, meaning = _select_daily_word(word_bank, length)
    
    return {
        "date": _get_daily_seed(),
        "word_bank": word_bank,
        "word_length": length,
        "meaning_hint": meaning[:20] + "..." if len(meaning) > 20 else meaning,
        "total_words": len(words),
    }


@router.get("/status")
async def get_daily_status(
    session: AsyncSession = Depends(get_session),
    word_bank: str = Query(default="CET4"),
    length: int = Query(default=5, ge=3, le=10),
) -> Dict[str, Any]:
    """Get current user daily challenge status."""
    from models import GameRecord
    from datetime import datetime, timedelta
    
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = start_of_day + timedelta(days=1)
    
    result = await session.execute(
        select(GameRecord)
        .where(
            GameRecord.created_at >= start_of_day,
            GameRecord.created_at < end_of_day,
        )
        .limit(1)
    )
    today_game = result.scalar_one_or_none()
    
    return {
        "date": _get_daily_seed(),
        "completed": today_game is not None,
        "status": today_game.status if today_game else None,
        "answer": today_game.answer_word if today_game else None,
    }
