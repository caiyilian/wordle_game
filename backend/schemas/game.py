from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RoomCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    word_bank: str = Field(default="CET4", min_length=1, max_length=20)
    word_length: int = Field(default=5, ge=3, le=10)
    max_players: int = Field(default=8, ge=1, le=20)


class RoomJoin(BaseModel):
    pass


class RoomResponse(BaseModel):
    id: str
    code: str
    name: str
    word_bank: str
    word_length: int
    status: str
    max_players: int
    player_count: int
    created_by: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class RoomListResponse(BaseModel):
    items: List[RoomResponse]
    total: int
    page: int
    page_size: int
