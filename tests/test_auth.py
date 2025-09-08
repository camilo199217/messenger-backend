from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_login():
    response = client.post(
        "/auth/register", data={"username": "user1", "password": "pass1"}
    )
    assert response.status_code == 200
    response = client.post(
        "/auth/login", data={"username": "user1", "password": "pass1"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
