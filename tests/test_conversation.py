"""Tests for Phase 3 Conversation Intelligence 2.0 endpoints & User Data Isolation.

Run with:  pytest tests/test_conversation.py -v
"""

import pytest


class TestConversationEndpoints:
    """CRUD operations on conversations."""

    def test_send_message_creates_conversation(self, client, auth_headers):
        resp = client.post(
            "/chat/message",
            json={"message": "Hello RajOS, summarize computer networks."},
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "conversation_id" in data
        assert "response" in data
        assert isinstance(data["conversation_id"], int)

    def test_list_conversations(self, client, auth_headers):
        # Create a conversation
        client.post(
            "/chat/message",
            json={"message": "Test conversation list prompt"},
            headers=auth_headers
        )
        resp = client.get("/chat/conversations", headers=auth_headers)
        assert resp.status_code == 200
        convs = resp.json()
        assert isinstance(convs, list)
        assert len(convs) >= 1
        assert "id" in convs[0]
        assert "title" in convs[0]

    def test_get_conversation_detail(self, client, auth_headers):
        msg_resp = client.post(
            "/chat/message",
            json={"message": "What is TCP/IP?"},
            headers=auth_headers
        )
        conv_id = msg_resp.json()["conversation_id"]

        resp = client.get(f"/chat/conversations/{conv_id}", headers=auth_headers)
        assert resp.status_code == 200
        detail = resp.json()
        assert detail["id"] == conv_id
        assert "messages" in detail
        assert len(detail["messages"]) >= 2  # user + assistant

    def test_rename_conversation(self, client, auth_headers):
        msg_resp = client.post(
            "/chat/message",
            json={"message": "Topic to be renamed"},
            headers=auth_headers
        )
        conv_id = msg_resp.json()["conversation_id"]

        resp = client.patch(
            f"/chat/conversations/{conv_id}",
            json={"title": "Computer Networks Study Session"},
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Computer Networks Study Session"
        assert data["user_title"] is True

    def test_archive_conversation(self, client, auth_headers):
        msg_resp = client.post(
            "/chat/message",
            json={"message": "Archive test prompt"},
            headers=auth_headers
        )
        conv_id = msg_resp.json()["conversation_id"]

        # Archive
        resp = client.patch(
            f"/chat/conversations/{conv_id}/archive",
            json={"archived": True},
            headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.json()["archived"] is True

        # Default list excludes archived
        list_resp = client.get("/chat/conversations", headers=auth_headers)
        ids = [c["id"] for c in list_resp.json()]
        assert conv_id not in ids

        # List with include_archived=true includes it
        list_archived = client.get("/chat/conversations?include_archived=true", headers=auth_headers)
        ids_archived = [c["id"] for c in list_archived.json()]
        assert conv_id in ids_archived

    def test_delete_single_conversation(self, client, auth_headers):
        msg_resp = client.post(
            "/chat/message",
            json={"message": "Delete single test prompt"},
            headers=auth_headers
        )
        conv_id = msg_resp.json()["conversation_id"]

        del_resp = client.delete(f"/chat/conversations/{conv_id}", headers=auth_headers)
        assert del_resp.status_code == 200

        # Subsequent GET should return 404
        get_resp = client.get(f"/chat/conversations/{conv_id}", headers=auth_headers)
        assert get_resp.status_code == 404

    def test_search_conversations(self, client, auth_headers):
        msg_resp = client.post(
            "/chat/message",
            json={"message": "Quantum Computing Fundamentals"},
            headers=auth_headers
        )
        conv_id = msg_resp.json()["conversation_id"]

        resp = client.get("/chat/search?q=Quantum", headers=auth_headers)
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) >= 1
        ids = [r["id"] for r in results]
        assert conv_id in ids


class TestUserIsolationSecurity:
    """Strict test verifying User B cannot access or modify User A's conversations."""

    def test_cross_user_isolation(self, client, auth_headers):
        # User 1 creates a conversation
        msg_resp = client.post(
            "/chat/message",
            json={"message": "User 1 private secret conversation"},
            headers=auth_headers
        )
        user1_conv_id = msg_resp.json()["conversation_id"]

        # Register and login User 2
        client.post("/register", json={
            "username": "user2_convo",
            "email": "user2_convo@example.com",
            "password": "SecurePass123!"
        })
        login_resp = client.post("/login", json={
            "email": "user2_convo@example.com",
            "password": "SecurePass123!"
        })
        token2 = login_resp.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User 2 attempts GET User 1's conversation -> MUST return 404
        resp_get = client.get(f"/chat/conversations/{user1_conv_id}", headers=headers2)
        assert resp_get.status_code == 404

        # User 2 attempts PATCH rename User 1's conversation -> MUST return 404
        resp_patch = client.patch(
            f"/chat/conversations/{user1_conv_id}",
            json={"title": "Hacked Title"},
            headers=headers2
        )
        assert resp_patch.status_code == 404

        # User 2 attempts DELETE User 1's conversation -> MUST return 404
        resp_del = client.delete(f"/chat/conversations/{user1_conv_id}", headers=headers2)
        assert resp_del.status_code == 404
