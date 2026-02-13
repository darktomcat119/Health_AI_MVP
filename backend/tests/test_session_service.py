"""Unit tests for the session service.

Tests session lifecycle: creation, retrieval, messages, and duration.
"""

import pytest
from datetime import datetime, timezone, timedelta

from app.exceptions import SessionExpiredException, SessionNotFoundException
from app.models.enums import RiskLevel
from app.repositories.memory_session import InMemorySessionRepository
from app.services.session_service import SessionService


class TestSessionService:
    """Tests for SessionService."""

    def test_creates_new_session(self, session_service: SessionService) -> None:
        """get_or_create with None should create a new session."""
        session = session_service.get_or_create(None)
        assert session.id.startswith("sess_")
        assert session.message_count == 0

    def test_retrieves_existing_session(self, session_service: SessionService) -> None:
        """get_or_create with existing ID should return the same session."""
        session = session_service.get_or_create(None)
        same_session = session_service.get_or_create(session.id)
        assert same_session.id == session.id

    def test_nonexistent_session_raises(self, session_service: SessionService) -> None:
        """get_session with unknown ID should raise SessionNotFoundException."""
        with pytest.raises(SessionNotFoundException):
            session_service.get_session("nonexistent_session_id")

    def test_add_message_updates_count(self, session_service: SessionService) -> None:
        """Adding a message should increment the message count."""
        session = session_service.get_or_create(None)
        session_service.add_user_message(session, "Hello", 10, RiskLevel.LOW)
        assert session.message_count == 1
        session_service.add_bot_message(session, "Hi there")
        assert session.message_count == 2

    def test_add_message_updates_risk_tracking(self, session_service: SessionService) -> None:
        """Adding user messages should update cumulative risk."""
        session = session_service.get_or_create(None)
        session_service.add_user_message(session, "I feel sad", 20, RiskLevel.LOW)
        session_service.add_user_message(session, "Very sad", 30, RiskLevel.MEDIUM)
        assert session.cumulative_risk == 50
        assert len(session.risk_scores) == 2

    def test_duration_calculation(self, session_service: SessionService) -> None:
        """Session duration should be non-negative."""
        session = session_service.get_or_create(None)
        assert session.duration_minutes >= 0

    def test_mark_triage_activated(self, session_service: SessionService) -> None:
        """mark_triage_activated should set the flag."""
        session = session_service.get_or_create(None)
        session_service.mark_triage_activated(session)
        assert session.triage_activated is True

    def test_mark_handoff(self, session_service: SessionService) -> None:
        """mark_handoff should set the flag."""
        session = session_service.get_or_create(None)
        session_service.mark_handoff(session)
        assert session.human_handoff is True
