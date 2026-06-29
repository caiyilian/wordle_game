from __future__ import annotations

import asyncio
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Manage WebSocket connections per room."""

    def __init__(self) -> None:
        # room_id -> {user_id -> websocket}
        self._rooms: dict[str, dict[str, WebSocket]] = {}
        # user_id -> room_id mapping for send_to
        self._user_room: dict[str, str] = {}
        self._lock = asyncio.Lock()

    async def connect(
        self,
        room_id: str,
        user_id: str,
        ws: WebSocket,
    ) -> None:
        async with self._lock:
            if room_id not in self._rooms:
                self._rooms[room_id] = {}
            self._rooms[room_id][user_id] = ws
            self._user_room[user_id] = room_id

    async def disconnect(
        self,
        room_id: str,
        user_id: str,
    ) -> None:
        async with self._lock:
            room_users = self._rooms.get(room_id)
            if room_users and user_id in room_users:
                del room_users[user_id]
                if not room_users:
                    del self._rooms[room_id]
                self._user_room.pop(user_id, None)

    async def broadcast(
        self,
        room_id: str,
        event: dict[str, Any],
        exclude_user_id: str | None = None,
    ) -> None:
        room_users = self._rooms.get(room_id)
        if not room_users:
            return
        serialized = self._serialize_event(event)
        tasks = []
        async with self._lock:
            for uid, ws in room_users.items():
                if uid == exclude_user_id:
                    continue
                tasks.append(self._safe_send(ws, serialized))
        await asyncio.gather(*tasks)

    async def send_to(
        self,
        user_id: str,
        event: dict[str, Any],
    ) -> bool:
        room_id = self._user_room.get(user_id)
        if not room_id:
            return False
        room_users = self._rooms.get(room_id)
        if not room_users or user_id not in room_users:
            return False
        ws = room_users[user_id]
        serialized = self._serialize_event(event)
        try:
            await ws.send_json(serialized)
            return True
        except Exception:
            return False

    async def send_to_room(
        self,
        room_id: str,
        event: dict[str, Any],
    ) -> int:
        """Send to all users in a room. Returns count of successful sends."""
        room_users = self._rooms.get(room_id)
        if not room_users:
            return 0
        serialized = self._serialize_event(event)
        tasks = []
        for ws in room_users.values():
            tasks.append(self._safe_send(ws, serialized))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return sum(1 for r in results if isinstance(r, bool) and r)

    async def _safe_send(
        self,
        ws: WebSocket,
        data: dict[str, Any],
    ) -> bool:
        try:
            await ws.send_json(data)
            return True
        except Exception:
            return False

    @staticmethod
    def _serialize_event(event: dict[str, Any]) -> dict[str, Any]:
        """Ensure event is JSON serializable."""
        return event

    async def get_room_users(self, room_id: str) -> list[str]:
        async with self._lock:
            room_users = self._rooms.get(room_id)
            if room_users:
                return list(room_users.keys())
            return []

    async def get_room_count(self, room_id: str) -> int:
        async with self._lock:
            room_users = self._rooms.get(room_id)
            if room_users:
                return len(room_users)
            return 0

    async def remove_user_from_all(self, user_id: str) -> list[str]:
        """Remove user from all rooms they're in. Returns list of room_ids."""
        removed_rooms = []
        async with self._lock:
            room_id = self._user_room.pop(user_id, None)
            if room_id and room_id in self._rooms:
                self._rooms[room_id].pop(user_id, None)
                removed_rooms.append(room_id)
                if not self._rooms[room_id]:
                    del self._rooms[room_id]
        return removed_rooms


# Global singleton
manager = ConnectionManager()
