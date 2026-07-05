"""End-to-end style tests for the authentication flow.

Run with:  pytest   (from the backend/ directory)
"""
import os
import tempfile

import pytest

# Use an isolated throwaway database for the test run.
os.environ["DB_PATH"] = os.path.join(tempfile.gettempdir(), "test_cloud_auth.db")
os.environ["SEED_DEMO_USER"] = "true"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-that-is-long-enough-32b"

from src import create_app  # noqa: E402  (import after env is set)


@pytest.fixture()
def client():
    if os.path.exists(os.environ["DB_PATH"]):
        os.remove(os.environ["DB_PATH"])
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def _login(client, email="test", password="test"):
    resp = client.post("/api/token", json={"email": email, "password": password})
    return resp


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_protected_route_requires_token(client):
    resp = client.get("/api/hello")
    assert resp.status_code == 401
    assert resp.get_json()["msg"] == "Missing Authorization Header"


def test_login_and_access(client):
    token = _login(client).get_json()["access_token"]
    resp = client.get("/api/hello", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "successfully logged in" in resp.get_json()["message"]


def test_login_bad_credentials(client):
    resp = _login(client, password="wrong")
    assert resp.status_code == 401


def test_register_and_login(client):
    resp = client.post(
        "/api/register",
        json={"email": "alice@example.com", "password": "s3cret", "display_name": "Alice"},
    )
    assert resp.status_code == 201
    token = _login(client, "alice@example.com", "s3cret").get_json()["access_token"]
    assert token

    me = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert me.get_json()["email"] == "alice@example.com"


def test_forbidden_on_other_users_file(client):
    # Demo user owns files 1 & 2. Register a second user who owns nothing.
    client.post("/api/register", json={"email": "bob@example.com", "password": "pw"})
    token = _login(client, "bob@example.com", "pw").get_json()["access_token"]
    resp = client.get("/api/files/1", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


def test_logout_revokes_token(client):
    token = _login(client).get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/hello", headers=headers).status_code == 200
    assert client.post("/api/logout", headers=headers).status_code == 200
    # Token is now revoked.
    assert client.get("/api/hello", headers=headers).status_code == 401
