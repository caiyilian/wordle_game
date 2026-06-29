from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    nickname: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    nickname: str
    password: str


class UserResponse(BaseModel):
    id: str
    nickname: str
    avatar_url: Optional[str]
    total_games: int
    wins: int
    current_streak: int
    max_streak: int
    guess_distribution: Dict[str, int]
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
