from fastapi.testclient import TestClient

from main import app


def _reg(c, base):
    import time
    ts = int(time.time() * 1000000) % 1000000
    nick = f'{base[:4]}{ts}'
    c.post("/api/users/register", json={"nickname": nick, "password": "secret123"})
    r = c.post("/api/users/login", json={"nickname": nick, "password": "secret123"})
    return r.json()["access_token"], nick


def test_get_leaderboard() -> None:
    with TestClient(app) as client:
        _reg(client, "lb1")
        _reg(client, "lb2")
        response = client.get("/api/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        # Check structure
        for entry in data[:1]:
            assert "rank" in entry
            assert "nickname" in entry
            assert "wins" in entry


def test_get_leaderboard_type() -> None:
    with TestClient(app) as client:
        _reg(client, "lb3")
        response = client.get("/api/leaderboard?type=streak")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
