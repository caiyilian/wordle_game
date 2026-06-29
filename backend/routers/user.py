from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token, decode_access_token, hash_password, verify_password
from database import get_session
from models import User
from schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse


router = APIRouter(prefix="/api/users", tags=["users"])
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def _token_response(user: User) -> TokenResponse:
    return TokenResponse(access_token=create_access_token(user.id), user=UserResponse.model_validate(user))


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    nickname = payload.nickname.strip()
    if not nickname:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Nickname is required")

    existing = await session.scalar(select(User).where(User.nickname == nickname))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nickname already exists")

    user = User(nickname=nickname, password_hash=hash_password(payload.password), guess_distribution={})
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    user = await session.scalar(select(User).where(User.nickname == payload.nickname.strip()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid nickname or password")
    return _token_response(user)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/me/stats", response_model=dict)
async def user_stats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    from models import GameRecord, PlayerGuess
    from sqlalchemy import select as sa_select

    # Get game stats from user model
    total_games = current_user.total_games
    wins = current_user.wins
    current_streak = current_user.current_streak
    max_streak = current_user.max_streak
    guess_distribution = current_user.guess_distribution or {}

    # Get recent games
    recent_result = await session.execute(
        sa_select(GameRecord)
        .where(GameRecord.id.in_(
            sa_select(PlayerGuess.game_id)
            .where(PlayerGuess.user_id == current_user.id)
            .distinct()
        ))
        .order_by(GameRecord.created_at.desc())
        .limit(10)
    )
    recent_games = recent_result.scalars().all()

    return {
        "total_games": total_games,
        "wins": wins,
        "win_rate": round(wins / max(total_games, 1) * 100, 1),
        "current_streak": current_streak,
        "max_streak": max_streak,
        "guess_distribution": {int(k): v for k, v in guess_distribution.items()},
        "recent_games": [
            {
                "id": g.id,
                "word_bank": g.word_bank,
                "answer_word": g.answer_word,
                "status": g.status,
                "created_at": g.created_at.isoformat() if g.created_at else None,
            }
            for g in recent_games
        ],
    }
