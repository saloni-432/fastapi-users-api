import pytest

class TestLogin:
    def test_valid_login_returns_token(self, client):
        r = client.post("/auth/token", data={"username": "alice", "password": "secret123"})
        assert r.status_code == 200
        assert "access_token" in r.json()
        assert r.json()["token_type"] == "bearer"

    def test_wrong_password_returns_401(self, client):
        r = client.post("/auth/token", data={"username": "alice", "password": "wrong"})
        assert r.status_code == 401

    def test_unknown_user_returns_401(self, client):
        r = client.post("/auth/token", data={"username": "nobody", "password": "pass"})
        assert r.status_code == 401

    def test_missing_password(self, client):
        r = client.post("/auth/token", data={"username": "alice"})
        assert r.status_code == 422

    def test_missing_username(self, client):
        r = client.post("/auth/token", data={"password": "secret123"})
        assert r.status_code == 422

    def test_error_has_detail(self, client):
        r = client.post("/auth/token", data={"username": "alice", "password": "bad"})
        assert "detail" in r.json()

class TestGetMe:
    def test_returns_200_with_token(self, client, auth_headers):
        r = client.get("/auth/me", headers=auth_headers)
        assert r.status_code == 200

    def test_returns_username(self, client, auth_headers):
        r = client.get("/auth/me", headers=auth_headers)
        assert r.json()["username"] == "alice"

    def test_no_token_returns_401(self, client):
        r = client.get("/auth/me")
        assert r.status_code == 401

    def test_invalid_token_returns_401(self, client):
        r = client.get("/auth/me", headers={"Authorization": "Bearer fake.token.here"})
        assert r.status_code == 401

class TestBackgroundRegister:
    def test_returns_200_when_authenticated(self, client, auth_headers):
        r = client.post("/auth/register-bg", headers=auth_headers)
        assert r.status_code == 200
        assert "message" in r.json()

    def test_requires_auth(self, client):
        r = client.post("/auth/register-bg")
        assert r.status_code == 401
