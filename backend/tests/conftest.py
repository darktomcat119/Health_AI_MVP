"""Shared test fixtures and factories.

Provides reusable fixtures for test sessions, service instances,
and the FastAPI test client. All fixtures are function-scoped
by default for test isolation.
"""

import os
import uuid
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import Settings, get_settings
from app.dependencies import (
    get_chatbot_service,
    get_risk_scorer,
    get_session_repository,
    get_session_service,
    get_triage_evaluator,
)
from app.main import create_app
from app.models.enums import RiskLevel, TriageStatus
from app.models.session import Session
from app.repositories.memory_session import InMemorySessionRepository
from app.services.chatbot import ChatbotService
from app.services.risk_scorer import RiskScorer
from app.services.session_service import SessionService
from app.services.triage_evaluator import TriageEvaluator


@pytest.fixture
def settings() -> Settings:
    """Provide test settings with defaults."""
    return get_settings()


@pytest.fixture
def session_repository() -> InMemorySessionRepository:
    """Provide a fresh in-memory session repository."""
    return InMemorySessionRepository()


@pytest.fixture
def session_service(session_repository: InMemorySessionRepository) -> SessionService:
    """Provide a session service with a fresh repository."""
    return SessionService(repository=session_repository)


@pytest.fixture
def risk_scorer() -> RiskScorer:
    """Provide a risk scorer instance."""
    return RiskScorer()


@pytest.fixture
def triage_evaluator() -> TriageEvaluator:
    """Provide a triage evaluator instance."""
    return TriageEvaluator()


@pytest.fixture
def chatbot_service() -> ChatbotService:
    """Provide a chatbot service instance."""
    return ChatbotService()


@pytest.fixture
def mock_session() -> Session:
    """Provide a clean session with no messages."""
    return create_session()


@pytest.fixture
def high_risk_session() -> Session:
    """Provide a session with elevated risk history."""
    session = create_session()
    session.add_message("user", "I feel hopeless", risk_score=65)
    session.update_risk(RiskLevel.HIGH)
    session.add_message("assistant", "I hear you.")
    session.add_message("user", "I can't go on", risk_score=70)
    session.update_risk(RiskLevel.HIGH)
    session.add_message("assistant", "Let's talk about this.")
    return session


def create_session(
    session_id: str | None = None,
    messages: int = 0,
    risk_level: RiskLevel = RiskLevel.LOW,
) -> Session:
    """Factory function to create test sessions.

    Args:
        session_id: Custom session ID, or None for auto-generated.
        messages: Number of placeholder messages to add.
        risk_level: Initial risk level for the session.

    Returns:
        Configured test Session instance.
    """
    sid = session_id or f"test_{uuid.uuid4().hex[:8]}"
    session = Session(id=sid)
    session.current_risk_level = risk_level

    for i in range(messages):
        if i % 2 == 0:
            session.add_message("user", f"Test message {i}", risk_score=10)
        else:
            session.add_message("assistant", f"Response {i}")

    return session


@pytest.fixture
def app():
    """Provide a fresh FastAPI app with isolated dependencies."""
    application = create_app()

    repo = InMemorySessionRepository()

    def override_repo():
        return repo

    def override_session_service():
        return SessionService(repository=repo)

    application.dependency_overrides[get_session_repository] = override_repo
    application.dependency_overrides[get_session_service] = override_session_service

    return application


@pytest.fixture
async def test_client(app):
    """Provide an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
