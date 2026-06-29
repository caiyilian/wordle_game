from fastapi.testclient import TestClient

from main import app


def test_get_daily_word() -> None:
    with TestClient(app) as client:
        response = client.get("/api/daily/word")
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "word_bank" in data
        assert "word_length" in data
        assert "meaning_hint" in data


def test_get_daily_word_custom() -> None:
    with TestClient(app) as client:
        response = client.get("/api/daily/word?word_bank=CET6&length=6")
        assert response.status_code == 200
        data = response.json()
        assert data["word_bank"] == "CET6"
        assert data["word_length"] == 6


def test_get_daily_word_not_found() -> None:
    with TestClient(app) as client:
        response = client.get("/api/daily/word?word_bank=NONEXISTENT&length=5")
        assert response.status_code == 404


def test_get_daily_status() -> None:
    with TestClient(app) as client:
        response = client.get("/api/daily/status")
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "completed" in data
