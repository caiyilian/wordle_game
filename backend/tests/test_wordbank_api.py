from fastapi.testclient import TestClient

from main import app


def test_get_wordbanks() -> None:
    with TestClient(app) as client:
        response = client.get("/api/wordbanks")
        assert response.status_code == 200
        banks = response.json()
        assert isinstance(banks, list)
        assert len(banks) > 0
        # Check structure
        for bank in banks:
            assert "name" in bank
            assert "lengths" in bank
            assert isinstance(bank["lengths"], dict)


def test_get_wordbank_info() -> None:
    with TestClient(app) as client:
        response = client.get("/api/wordbanks/info/CET4")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "CET4"
        assert "lengths" in data


def test_get_wordbank_info_not_found() -> None:
    with TestClient(app) as client:
        response = client.get("/api/wordbanks/info/NONEXISTENT")
        assert response.status_code == 404
