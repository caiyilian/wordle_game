import time
from typing import Dict

from fastapi.testclient import TestClient

from main import app


def _nick(base: str) -> str:
    ts = int(time.time() * 1000) % 10000
    return f"{base[:6]}{ts}"


def test_register_returns_user_and_token_without_password() -> None:
    with TestClient(app) as client:
        response = client.post("/api/users/register", json={"nickname": _nick("p3_reg"), "password": "secret123"})

    assert response.status_code == 201
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["user"]["nickname"]
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]


def test_duplicate_nickname_returns_400() -> None:
    with TestClient(app) as client:
        name = _nick("p3_dup")
        client.post("/api/users/register", json={"nickname": name, "password": "secret123"})
        response = client.post("/api/users/register", json={"nickname": name, "password": "secret456"})

    assert response.status_code == 400


def test_login_and_me_with_token() -> None:
    with TestClient(app) as client:
        name = _nick("p3_log")
        client.post("/api/users/register", json={"nickname": name, "password": "secret123"})
        login_response = client.post("/api/users/login", json={"nickname": name, "password": "secret123"})
        token = login_response.json()["access_token"]
        me_response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})

    assert login_response.status_code == 200
    assert me_response.status_code == 200
    assert me_response.json()["nickname"] == name


def test_login_with_wrong_password_returns_401() -> None:
    with TestClient(app) as client:
        name = _nick("p3_wrp")
        client.post("/api/users/register", json={"nickname": name, "password": "secret123"})
        response = client.post("/api/users/login", json={"nickname": name, "password": "wrong-password"})

    assert response.status_code == 401


def test_me_without_token_returns_401() -> None:
    with TestClient(app) as client:
        response = client.get("/api/users/me")

    assert response.status_code == 401
