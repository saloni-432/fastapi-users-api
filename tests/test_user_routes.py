import pytest


class TestGetUsers:
    def test_returns_200(self, client):
        r = client.get("/users/")
        assert r.status_code == 200

    def test_returns_list(self, client):
        r = client.get("/users/")
        assert isinstance(r.json()["data"], list)

    def test_empty_initially(self, client):
        r = client.get("/users/")
        assert r.json()["data"] == []

    def test_lists_created_user(self, client):
        client.post(
            "/users/",
            json={"name": "Bob", "email": "bob@test.com"}
        )

        users = client.get("/users/").json()["data"]
        emails = [u["email"] for u in users]

        assert "bob@test.com" in emails


class TestGetUser:
    def test_returns_correct_user(self, client, existing_user):
        r = client.get(f"/users/{existing_user.id}")

        assert r.status_code == 200
        assert r.json()["data"]["email"] == existing_user.email

    def test_missing_user(self, client):
        r = client.get("/users/999999")

        assert r.status_code == 200
        assert r.json() == {"message": "User not found"}

    def test_invalid_id_type(self, client):
        r = client.get("/users/abc")
        assert r.status_code == 422


class TestCreateUser:
    def test_creates_successfully(self, client):
        r = client.post(
            "/users/",
            json={"name": "Bob", "email": "bob@test.com"}
        )

        assert r.status_code == 200
        assert r.json()["email"] == "bob@test.com"

    def test_missing_name(self, client):
        r = client.post("/users/", json={"email": "bob@test.com"})
        assert r.status_code == 422

    def test_missing_email(self, client):
        r = client.post("/users/", json={"name": "Bob"})
        assert r.status_code == 422

    def test_empty_body(self, client):
        r = client.post("/users/", json={})
        assert r.status_code == 422


class TestUpdateUser:
    def test_updates_user(self, client, existing_user):
        r = client.put(
            f"/users/{existing_user.id}",
            json={
                "name": "Updated",
                "email": "updated@test.com"
            }
        )

        assert r.status_code == 200
        assert r.json()["name"] == "Updated"

    def test_missing_user(self, client):
        r = client.put(
            "/users/999999",
            json={
                "name": "X",
                "email": "x@test.com"
            }
        )

        assert r.json() == {"error": "User not found"}


class TestDeleteUser:
    def test_deletes_user(self, client, existing_user):
        r = client.delete(f"/users/{existing_user.id}")

        assert r.status_code == 200
        assert r.json() == {
            "message": "User deleted successfully"
        }

    def test_user_gone_after_delete(self, client, existing_user):
        client.delete(f"/users/{existing_user.id}")

        r = client.get(f"/users/{existing_user.id}")
        data = r.json()

        # handle cached or non-cached response
        if "data" in data:
            assert data["data"]["id"] != existing_user.id
        else:
            assert data == {"message": "User not found"}

    def test_missing_user(self, client):
        r = client.delete("/users/999999")

        assert r.json() == {"error": "User not found"}