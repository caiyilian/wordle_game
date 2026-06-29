import time
from typing import Dict

from fastapi.testclient import TestClient

from main import app


def _nick(base: str) -> str:
    ts = int(time.time() * 1000) % 10000
    return f"{base[:6]}{ts}"


def register(client: TestClient, base_nickname: str) -> str:
    response = client.post("/api/users/register", json={"nickname": _nick(base_nickname), "password": "secret123"})
    assert response.status_code == 201, f"Register failed: {response.json()}"
    return response.json()["access_token"]


def auth(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_create_list_and_get_room() -> None:
    with TestClient(app) as client:
        token = register(client, "p4_owner")
        create_response = client.post(
            "/api/rooms",
            headers=auth(token),
            json={"name": "Daily Room", "word_bank": "CET4", "word_length": 5, "max_players": 3},
        )
        room = create_response.json()
        list_response = client.get("/api/rooms")
        detail_response = client.get(f"/api/rooms/{room['code']}")

    assert create_response.status_code == 201
    assert len(room["code"]) == 6
    assert room["player_count"] == 1
    assert any(item["id"] == room["id"] for item in list_response.json()["items"])
    assert detail_response.status_code == 200
    assert detail_response.json()["code"] == room["code"]


def test_join_duplicate_join_full_and_leave_room() -> None:
    with TestClient(app) as client:
        owner_token = register(client, "p4_own1")
        second_token = register(client, "p4_sec2")
        third_token = register(client, "p4_thr3")
        room = client.post(
            "/api/rooms",
            headers=auth(owner_token),
            json={"name": "Tiny Room", "word_bank": "CET4", "word_length": 5, "max_players": 2},
        ).json()

        join_response = client.post(f"/api/rooms/{room['code']}/join", headers=auth(second_token))
        duplicate_response = client.post(f"/api/rooms/{room['code']}/join", headers=auth(second_token))
        full_response = client.post(f"/api/rooms/{room['code']}/join", headers=auth(third_token))
        leave_response = client.post(f"/api/rooms/{room['code']}/leave", headers=auth(second_token))

    assert join_response.status_code == 200
    assert join_response.json()["player_count"] == 2
    assert duplicate_response.status_code == 400
    assert full_response.status_code == 400
    assert leave_response.status_code == 200
    assert leave_response.json()["player_count"] == 1
