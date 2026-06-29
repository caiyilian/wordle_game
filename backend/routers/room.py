from typing import Optional

import random
import string

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import Room, RoomMember, User
from routers.user import get_current_user
from schemas.game import RoomCreate, RoomListResponse, RoomResponse


router = APIRouter(prefix="/api/rooms", tags=["rooms"])


def _make_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(6))


async def _generate_unique_code(session: AsyncSession) -> str:
    for _ in range(20):
        code = _make_code()
        existing = await session.scalar(select(Room.id).where(Room.code == code))
        if existing is None:
            return code
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not generate room code")


async def _get_room(identifier: str, session: AsyncSession) -> Room:
    room = await session.get(Room, identifier)
    if room is None:
        room = await session.scalar(select(Room).where(Room.code == identifier.upper()))
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room


async def _player_count(room_id: str, session: AsyncSession) -> int:
    return int(await session.scalar(select(func.count()).select_from(RoomMember).where(RoomMember.room_id == room_id)) or 0)


async def _room_response(room: Room, session: AsyncSession) -> RoomResponse:
    return RoomResponse(
        id=room.id,
        code=room.code,
        name=room.name,
        word_bank=room.word_bank,
        word_length=room.word_length,
        status=room.status,
        max_players=room.max_players,
        player_count=await _player_count(room.id, session),
        created_by=room.created_by,
        created_at=room.created_at,
    )


async def _membership(room_id: str, user_id: str, session: AsyncSession) -> Optional[RoomMember]:
    return await session.scalar(
        select(RoomMember).where(RoomMember.room_id == room_id, RoomMember.user_id == user_id)
    )


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    payload: RoomCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> RoomResponse:
    room = Room(
        code=await _generate_unique_code(session),
        name=payload.name.strip(),
        word_bank=payload.word_bank,
        word_length=payload.word_length,
        max_players=payload.max_players,
        created_by=current_user.id,
    )
    session.add(room)
    await session.flush()
    session.add(RoomMember(room_id=room.id, user_id=current_user.id))
    await session.commit()
    await session.refresh(room)
    return await _room_response(room, session)


@router.get("", response_model=RoomListResponse)
async def list_rooms(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> RoomListResponse:
    total = int(await session.scalar(select(func.count()).select_from(Room)) or 0)
    rooms = (
        await session.scalars(
            select(Room).order_by(Room.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
    ).all()
    return RoomListResponse(
        items=[await _room_response(room, session) for room in rooms],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{identifier}", response_model=RoomResponse)
async def get_room(identifier: str, session: AsyncSession = Depends(get_session)) -> RoomResponse:
    return await _room_response(await _get_room(identifier, session), session)


@router.post("/{identifier}/join", response_model=RoomResponse)
async def join_room(
    identifier: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> RoomResponse:
    room = await _get_room(identifier, session)
    if await _membership(room.id, current_user.id, session) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already joined room")

    if await _player_count(room.id, session) >= room.max_players:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room is full")

    session.add(RoomMember(room_id=room.id, user_id=current_user.id))
    await session.commit()
    await session.refresh(room)
    return await _room_response(room, session)


@router.post("/{identifier}/leave", response_model=RoomResponse)
async def leave_room(
    identifier: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> RoomResponse:
    room = await _get_room(identifier, session)
    membership = await _membership(room.id, current_user.id, session)
    if membership is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not in room")

    await session.delete(membership)
    await session.commit()
    await session.refresh(room)
    return await _room_response(room, session)
