"""
Shared pytest fixtures for RajOS test suite.

- Uses an in-memory SQLite database (no disk writes, no rajos.db involvement).
- Overrides SECRET_KEY with a test-safe value.
- Provides `client` fixture with a registered+logged-in test user.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.pool import StaticPool
import app.database.connection as db_conn

# Override env vars BEFORE importing app modules so settings picks them up.
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["DEBUG"] = "true"

from app.database.connection import Base, get_db  # noqa: E402
from app.models.user import User  # noqa: F401, E402
from app.models.task import Task  # noqa: F401, E402
from app.models.note import Note  # noqa: F401, E402
from app.models.memory import Memory  # noqa: F401, E402
from app.models.document import Document  # noqa: F401, E402
from app.models.conversation import Conversation  # noqa: F401, E402
from app.models.message import Message  # noqa: F401, E402
from app.models.preference import UserPreference  # noqa: F401, E402
from app.automation.automation_models import Automation  # noqa: F401, E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def engine():
    """In-memory SQLite engine — shared across all tests in the session."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    db_conn.engine = test_engine
    yield test_engine
    test_engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine):
    """Provide a clean database session for each test function."""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient with overridden get_db pointing at in-memory database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(client):
    """Register a test user and return bearer token headers."""
    # Register
    client.post("/register", json={
        "username": "testuser",
        "email": "test@rajos.io",
        "password": "TestPassword123!"
    })
    # Login
    resp = client.post("/login", json={
        "email": "test@rajos.io",
        "password": "TestPassword123!"
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
