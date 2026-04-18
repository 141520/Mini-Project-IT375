"""Basic API smoke tests."""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_games_public():
    r = client.get("/api/v1/games")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_chat_requires_auth():
    r = client.post("/api/v1/chat", json={"game_id": 1, "question": "hi"})
    assert r.status_code == 401


def test_admin_requires_auth():
    r = client.get("/api/v1/admin/stats")
    assert r.status_code == 401
