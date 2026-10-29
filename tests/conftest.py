"""
Shared pytest fixtures for RajOS test suite.

- API/session fixtures use an in-memory SQLite database (no rajos.db access).
- The application engine (Tool Registry, scheduler, background threads) is
  pointed at a throw-away temp file database so every thread sees the same
  schema — tests never touch the real ./rajos.db.
- Overrides SECRET_KEY with a test-safe value.
- Provides `client` fixture with a registered+logged-in test user.
"""

import os
import tempfile
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.pool import StaticPool

# Override env vars BEFORE importing ANY app module so settings — and the
# database engine — pick them up (tests must never touch rajos.db).
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only"
os.environ["DEBUG"] = "true"

# The app-level engine is shared by tools, the scheduler and worker threads.
# A temp file DB behaves like production SQLite (one DB, many connections).
_APP_TEST_DB = os.path.join(tempfile.gettempdir(), f"rajos_test_app_{uuid.uuid4().hex[:8]}.db")
if os.path.exists(_APP_TEST_DB):
    os.remove(_APP_TEST_DB)
os.environ["DATABASE_URL"] = f"sqlite:///{_APP_TEST_DB}"

import app.database.connection as db_conn  # noqa: E402
from app.database.connection import Base, get_db  # noqa: E402
from app.models.user import User  # noqa: F401, E402
from app.models.task import Task  # noqa: F401, E402
from app.models.note import Note  # noqa: F401, E402
from app.models.memory import Memory  # noqa: F401, E402
from app.models.document import Document  # noqa: F401, E402
from app.models.conversation import Conversation  # noqa: F401, E402
from app.models.message import Message  # noqa: F401, E402
from app.models.preference import UserPreference  # noqa: F401, E402
from app.automation.automation_models import Automation, AutomationRun  # noqa: F401, E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _cleanup_app_test_db():
    """Remove the throw-away application database after the test session."""
    yield
    try:
        db_conn.engine.dispose()
        if os.path.exists(_APP_TEST_DB):
            os.remove(_APP_TEST_DB)
    except OSError:
        pass


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
def test_user(db_session):
    """A fresh, isolated test user (unique per test) in the test database."""
    import uuid
    from app.models.user import User

    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"fixtureuser_{suffix}",
        email=f"fixtureuser_{suffix}@rajos.io",
        password="TestPassword123!",
        notifications_enabled=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


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
