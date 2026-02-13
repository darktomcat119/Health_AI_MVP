"""Integration tests for API endpoints.

Tests the full request/response cycle through the FastAPI application.
"""

import pytest

from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Tests for GET /api/v1/health."""

    async def test_health_returns_ok(self, test_client: AsyncClient) -> None:
        """Health endpoint should return healthy status."""
        response = await test_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    async def test_health_shows_session_count(self, test_client: AsyncClient) -> None:
        """Health endpoint should show active session count."""
        response = await test_client.get("/api/v1/health")
        data = response.json()
        assert "active_sessions" in data
        assert isinstance(data["active_sessions"], int)


@pytest.mark.asyncio
class TestChatEndpoint:
    """Tests for POST /api/v1/chat/."""

    async def test_chat_creates_session(self, test_client: AsyncClient) -> None:
        """First message should create a new session."""
        response = await test_client.post(
            "/api/v1/chat/",
            json={"user_message": "Hello there"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["session_id"].startswith("sess_")

    async def test_chat_continues_session(self, test_client: AsyncClient) -> None:
        """Subsequent messages should continue the same session."""
        first = await test_client.post(
            "/api/v1/chat/",
            json={"user_message": "Hello"},
        )
        session_id = first.json()["session_id"]

        second = await test_client.post(
            "/api/v1/chat/",
            json={"session_id": session_id, "user_message": "I feel stressed"},
        )
        assert second.json()["session_id"] == session_id
        assert second.json()["session_message_count"] == 4  # user+bot x2

    async def test_chat_returns_all_required_fields(self, test_client: AsyncClient) -> None:
        """Chat response should include all required fields."""
        response = await test_client.post(
            "/api/v1/chat/",
            json={"user_message": "How are you?"},
        )
        data = response.json()
        required_fields = [
            "session_id", "bot_response", "risk_score", "risk_level",
            "triage_activated", "human_handoff", "session_message_count", "timestamp",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    async def test_chat_risk_score_in_range(self, test_client: AsyncClient) -> None:
        """Risk score should be between 0 and 100."""
        response = await test_client.post(
            "/api/v1/chat/",
            json={"user_message": "I feel overwhelmed"},
        )
        data = response.json()
        assert 0 <= data["risk_score"] <= 100

    async def test_high_risk_triggers_triage(self, test_client: AsyncClient) -> None:
        """High-risk messages should trigger triage."""
        response = await test_client.post(
            "/api/v1/chat/",
            json={"user_message": "I want to kill myself, i give up, everything is terrible awful horrible miserable and hopeless"},
        )
        data = response.json()
        assert data["triage_activated"] is True
        assert data["human_handoff"] is True


@pytest.mark.asyncio
class TestHistoryEndpoint:
    """Tests for GET /api/v1/chat/{session_id}/history."""

    async def test_history_returns_messages(self, test_client: AsyncClient) -> None:
        """History should return all messages in a session."""
        chat_response = await test_client.post(
            "/api/v1/chat/",
            json={"user_message": "Hello there"},
        )
        session_id = chat_response.json()["session_id"]

        history_response = await test_client.get(f"/api/v1/chat/{session_id}/history")
        assert history_response.status_code == 200
        data = history_response.json()
        assert len(data["history"]) == 2  # user message + bot response
        assert data["message_count"] == 2

    async def test_history_404_for_unknown_session(self, test_client: AsyncClient) -> None:
        """History for unknown session should return 404."""
        response = await test_client.get("/api/v1/chat/unknown_session/history")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestHandoffEndpoint:
    """Tests for POST /api/v1/chat/{session_id}/handoff."""

    async def test_handoff_returns_context(self, test_client: AsyncClient) -> None:
        """Handoff should return professional context."""
        chat_response = await test_client.post(
            "/api/v1/chat/",
            json={"user_message": "I need help"},
        )
        session_id = chat_response.json()["session_id"]

        handoff_response = await test_client.post(
            f"/api/v1/chat/{session_id}/handoff",
        )
        assert handoff_response.status_code == 200
        data = handoff_response.json()
        assert data["handoff_status"] == "initiated"
        assert "professional_context" in data
        assert "message_count" in data["professional_context"]
