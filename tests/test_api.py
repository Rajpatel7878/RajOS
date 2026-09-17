"""
Tests for core API endpoints: health, readiness, and auth.
"""

import pytest


class TestHealth:
    """GET /health — must always return 200."""

    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_body_has_status(self, client):
        data = client.get("/health").json()
        assert data["status"] == "healthy"

    def test_health_body_has_app_name(self, client):
        data = client.get("/health").json()
        assert "app" in data


class TestReadiness:
    """GET /readiness — verifies database connectivity."""

    def test_readiness_returns_200(self, client):
        resp = client.get("/readiness")
        assert resp.status_code == 200

    def test_readiness_has_database_field(self, client):
        data = client.get("/readiness").json()
        assert "database" in data


class TestRoot:
    """GET / — identification endpoint."""

    def test_root_returns_200(self, client):
        assert client.get("/").status_code == 200

    def test_root_has_docs_field(self, client):
        data = client.get("/").json()
        assert "docs" in data


class TestRegistration:
    """POST /register — user creation."""

    def test_register_success(self, client):
        resp = client.post("/register", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "newuser@example.com"
        # Password must never be returned
        assert "password" not in data

    def test_register_duplicate_email_returns_400(self, client):
        payload = {
            "username": "dupuser",
            "email": "dup@example.com",
            "password": "SecurePass123!"
        }
        client.post("/register", json=payload)
        resp = client.post("/register", json=payload)
        assert resp.status_code == 400

    def test_register_invalid_email_returns_422(self, client):
        resp = client.post("/register", json={
            "username": "baduser",
            "email": "not-an-email",
            "password": "SecurePass123!"
        })
        assert resp.status_code == 422


class TestLogin:
    """POST /login — authentication."""

    def test_login_success(self, client):
        client.post("/register", json={
            "username": "logintest",
            "email": "logintest@example.com",
            "password": "SecurePass123!"
        })
        resp = client.post("/login", json={
            "email": "logintest@example.com",
            "password": "SecurePass123!"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password_returns_401(self, client):
        client.post("/register", json={
            "username": "wrongpass",
            "email": "wrongpass@example.com",
            "password": "CorrectPassword!"
        })
        resp = client.post("/login", json={
            "email": "wrongpass@example.com",
            "password": "WrongPassword!"
        })
        assert resp.status_code == 401

    def test_login_unknown_email_returns_404(self, client):
        resp = client.post("/login", json={
            "email": "nobody@example.com",
            "password": "SomePassword!"
        })
        assert resp.status_code == 404


class TestProtectedRoute:
    """Protected routes must reject unauthenticated requests with 403."""

    def test_tasks_requires_auth(self, client):
        resp = client.get("/tasks/")
        assert resp.status_code in (401, 403)

    def test_notes_requires_auth(self, client):
        resp = client.get("/notes/")
        assert resp.status_code in (401, 403)

    def test_memory_requires_auth(self, client):
        resp = client.get("/memory/")
        assert resp.status_code in (401, 403)

    def test_dashboard_stats_requires_auth(self, client):
        resp = client.get("/dashboard/stats")
        assert resp.status_code in (401, 403)


class TestTasksAuthenticated:
    """Task CRUD with authentication."""

    def test_create_task(self, client, auth_headers):
        resp = client.post("/tasks/", json={"title": "Write tests"}, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Write tests"

    def test_get_tasks(self, client, auth_headers):
        resp = client.get("/tasks/", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_user_data_isolation(self, client, auth_headers, db_session):
        """Tasks created by one user must not appear for another."""
        # Register second user
        client.post("/register", json={
            "username": "user2",
            "email": "user2@example.com",
            "password": "SecurePass123!"
        })
        resp2 = client.post("/login", json={
            "email": "user2@example.com",
            "password": "SecurePass123!"
        })
        token2 = resp2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User 1 creates a task
        client.post("/tasks/", json={"title": "User1 private task"}, headers=auth_headers)

        # User 2 should not see user 1's tasks
        resp = client.get("/tasks/", headers=headers2)
        assert resp.status_code == 200
        user2_tasks = resp.json()
        titles = [t["title"] for t in user2_tasks]
        assert "User1 private task" not in titles
