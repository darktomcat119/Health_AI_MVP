"""FastAPI dependency injection providers.

Provides singleton service instances via FastAPI's Depends() system.
Each provider function is designed to be used as a dependency in route handlers.
"""

from functools import lru_cache

from app.repositories.memory_session import InMemorySessionRepository
from app.services.anonymizer import Anonymizer
from app.services.chatbot import ChatbotService
from app.services.risk_scorer import RiskScorer
from app.services.session_service import SessionService
from app.services.triage_evaluator import TriageEvaluator


@lru_cache
def get_session_repository() -> InMemorySessionRepository:
    """Provide the singleton session repository.

    Returns:
        InMemorySessionRepository: Thread-safe in-memory session store.
    """
    return InMemorySessionRepository()


@lru_cache
def get_risk_scorer() -> RiskScorer:
    """Provide the singleton risk scorer.

    Returns:
        RiskScorer: Multi-signal risk scoring engine.
    """
    return RiskScorer()


@lru_cache
def get_triage_evaluator() -> TriageEvaluator:
    """Provide the singleton triage evaluator.

    Returns:
        TriageEvaluator: Cascading triage rule engine.
    """
    return TriageEvaluator()


@lru_cache
def get_anonymizer() -> Anonymizer:
    """Provide the singleton anonymizer.

    Returns:
        Anonymizer: PII stripping service.
    """
    return Anonymizer()


@lru_cache
def get_chatbot_service() -> ChatbotService:
    """Provide the singleton chatbot service.

    Returns:
        ChatbotService: LLM orchestrator with response validation.
    """
    return ChatbotService(anonymizer=get_anonymizer())


def get_session_service() -> SessionService:
    """Provide a session service instance.

    Returns:
        SessionService: Session lifecycle management service.
    """
    return SessionService(repository=get_session_repository())
