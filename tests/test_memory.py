import pytest
from app.memory.memory_validator import memory_validator
from app.memory.memory_service import memory_service
from app.models.memory import Memory


def test_memory_validator_secrets():
    """Verify secrets and credentials are rejected."""
    valid, reason = memory_validator.validate("api_key", "sk-1234567890abcdef1234567890abcdef")
    assert not valid
    assert "sensitive" in reason.lower()

    valid, reason = memory_validator.validate("db_pass", "password = supersecret")
    assert not valid

    valid, reason = memory_validator.validate("my_preference", "I prefer Python")
    assert valid


def test_memory_validator_transient():
    """Verify transient commands and greetings are rejected."""
    valid, reason = memory_validator.validate("greeting", "hello how are you")
    assert not valid
    assert "transient" in reason.lower()

    valid, reason = memory_validator.validate("time", "what time is it")
    assert not valid

    valid, reason = memory_validator.validate("rule", "Always respond in markdown")
    assert valid


def test_memory_crud_and_deduplication(db_session):
    """Test Memory 2.0 CRUD, deduplication, and conflict resolution."""
    user_id = 9991

    # 1. Create initial memory
    res1 = memory_service.create_memory(
        db=db_session,
        user_id=user_id,
        key="Favorite Framework",
        value="FastAPI",
        memory_type="preference"
    )
    assert res1["status"] == "created"
    mem1 = res1["memory"]
    assert mem1.key == "Favorite Framework"
    assert mem1.value == "FastAPI"

    # 2. Duplicate creation -> ignored
    res2 = memory_service.create_memory(
        db=db_session,
        user_id=user_id,
        key="Favorite Framework",
        value="FastAPI",
        memory_type="preference"
    )
    assert res2["status"] == "ignored"

    # 3. Same key, updated value -> update conflict resolution
    res3 = memory_service.create_memory(
        db=db_session,
        user_id=user_id,
        key="Favorite Framework",
        value="FastAPI + Pydantic v2",
        memory_type="preference"
    )
    assert res3["status"] == "updated"
    assert res3["memory"].id == mem1.id
    assert res3["memory"].value == "FastAPI + Pydantic v2"


def test_explicit_memory_intents(db_session):
    """Test explicit remember and forget intent parsing."""
    user_id = 9992

    # Explicit Remember
    handled, msg, mem = memory_service.parse_and_handle_explicit_intent(
        db=db_session,
        user_id=user_id,
        user_message="Remember that I work as a Lead Architect"
    )
    assert handled
    assert mem is not None
    assert "Lead Architect" in mem.value

    # Explicit Forget
    handled_f, msg_f, mem_f = memory_service.parse_and_handle_explicit_intent(
        db=db_session,
        user_id=user_id,
        user_message="Forget my role as Lead Architect"
    )
    assert handled_f
    assert "Forgot memory" in msg_f or "No matching" in msg_f


def test_user_data_isolation_api(client, auth_headers, db_session):
    """Verify REST endpoints enforce strict user data isolation."""
    # User 1 creates memory via API
    resp1 = client.post("/memory/", json={
        "key": "Secret Project",
        "value": "Project Titan",
        "memory_type": "project"
    }, headers=auth_headers)
    assert resp1.status_code == 201
    mem_id = resp1.json()["id"]

    # Register User 2 with unique email & username
    client.post("/register", json={
        "username": "user2_mem_iso",
        "email": "user2_mem_iso@rajos.io",
        "password": "Password123!"
    })
    login_resp = client.post("/login", json={
        "email": "user2_mem_iso@rajos.io",
        "password": "Password123!"
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token2 = login_resp.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # User 2 list memories -> should NOT see User 1's memory
    resp2 = client.get("/memory/", headers=headers2)
    assert resp2.status_code == 200
    user2_mems = resp2.json()
    assert all(m["id"] != mem_id for m in user2_mems)

    # User 2 direct fetch User 1's memory -> 404
    resp3 = client.get(f"/memory/{mem_id}", headers=headers2)
    assert resp3.status_code == 404
