import time
from typing import Dict

from starlette.websockets import WebSocketDisconnect
from fastapi.testclient import TestClient

from main import app


def _nick(base: str) -> str:
    ts = int(time.time() * 1000) % 10000
    return f"{base[:6]}{ts}"


def _register_and_login(client: TestClient, base: str) -> tuple:
    nick = _nick(base)
    client.post("/api/users/register", json={"nickname": nick, "password": "secret123"})
    resp = client.post("/api/users/login", json={"nickname": nick, "password": "secret123"})
    return resp.json()["access_token"], nick


def auth_header(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_websocket_ping_pong() -> None:
    with TestClient(app) as client:
        token, _ = _register_and_login(client, "ws_user1")
        with client.websocket_connect(f"/ws/testroom?token={token}") as ws:
            ws.send_json({"type": "ping"})
            data = ws.receive_json()
            assert data["type"] == "pong"


def test_websocket_invalid_token_rejected() -> None:
    with TestClient(app) as client:
        try:
            client.websocket_connect("/ws/testroom?token=invalidtoken12345")
        except WebSocketDisconnect as exc:
            assert exc.code == 4001
