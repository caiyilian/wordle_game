from __future__ import annotations

from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.security import decode_access_token
from ws.manager import manager

router = APIRouter(tags=["websocket"])


def _make_event(event_type: str, **kwargs: Any) -> dict[str, Any]:
    event: dict[str, Any] = {"type": event_type}
    event.update(kwargs)
    return event


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: str,
) -> None:
    # Validate JWT token
    user_id = decode_access_token(token)
    if user_id is None:
        await websocket.close(code=4001, reason="Invalid token")
        return

    # Accept connection
    await websocket.accept()

    # Register connection
    await manager.connect(room_id, user_id, websocket)

    # Notify others in room
    await manager.broadcast(
        room_id,
        _make_event("player_joined", user_id=user_id),
        exclude_user_id=user_id,
    )

    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            if event_type == "ping":
                await websocket.send_json(_make_event("pong"))
            elif event_type == "guess":
                # Forward guess to room for Phase 6
                await manager.broadcast(
                    room_id,
                    _make_event("guess", user_id=user_id, word=data.get("word", "")),
                )
            elif event_type == "chat":
                # Forward chat message to room
                message = data.get("message", "")
                if message:
                    await manager.broadcast(
                        room_id,
                        _make_event("chat", user_id=user_id, message=message),
                    )
            elif event_type == "leave":
                break
            else:
                # Unknown event type
                pass

    except WebSocketDisconnect:
        pass
    finally:
        # Clean up on disconnect
        await manager.disconnect(room_id, user_id)
        await manager.broadcast(
            room_id,
            _make_event("player_left", user_id=user_id),
        )
