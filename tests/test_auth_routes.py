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

class TestRoleBasedAccess:
    def test_admin_only_requires_auth(self, client):
        response = client.get("/auth/admin-only")

        assert response.status_code == 401

    def test_admin_only_rejects_regular_user(self, client):
        login_response = client.post(
            "/auth/token",
            data={
                "username": "alice",
                "password": "secret123",
            },
        )
        assert login_response.status_code == 200

        access_token = login_response.json()["access_token"]

        response = client.get(
            "/auth/admin-only",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Admin access required"

    def test_admin_only_allows_admin(self, client):
        login_response = client.post(
            "/auth/token",
            data={
                "username": "admin",
                "password": "admin123",
            },
        )
        assert login_response.status_code == 200

        access_token = login_response.json()["access_token"]

        response = client.get(
            "/auth/admin-only",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        assert response.json()["username"] == "admin"


class TestRefreshAndLogout:
    def test_refresh_returns_new_token_pair(self, client):
        login_response = client.post(
            "/auth/token",
            data={
                "username": "alice",
                "password": "secret123",
            },
        )
        assert login_response.status_code == 200

        old_refresh_token = login_response.json()["refresh_token"]

        refresh_response = client.post(
            "/auth/refresh",
            json={"refresh_token": old_refresh_token},
        )

        assert refresh_response.status_code == 200
        assert "access_token" in refresh_response.json()
        assert "refresh_token" in refresh_response.json()

    def test_logout_invalidates_refresh_token(self, client):
        login_response = client.post(
            "/auth/token",
            data={
                "username": "alice",
                "password": "secret123",
            },
        )
        assert login_response.status_code == 200

        tokens = login_response.json()

        logout_response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert logout_response.status_code == 200

        refresh_response = client.post(
            "/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )

        assert refresh_response.status_code == 401
