"""Session business logic service.

Manages session lifecycle: creation, retrieval, message tracking,
and duration monitoring. Delegates storage to the repository layer.
"""

import logging
from datetime import datetime, timezone

from app.exceptions import SessionExpiredException, SessionNotFoundException
from app.config import get_settings
from app.models.enums import RiskLevel
from app.models.session import Session
from app.repositories.memory_session import InMemorySessionRepository

logger = logging.getLogger(__name__)


class SessionService:
    """Manages conversation session lifecycle and state.

    Args:
        repository: Session storage implementation.
    """

    def __init__(self, repository: InMemorySessionRepository) -> None:
        self._repository = repository

    def get_or_create(self, session_id: str | None) -> Session:
        """Retrieve an existing session or create a new one.

        Args:
            session_id: Existing session ID, or None to start a new conversation.

        Returns:
            The active session.

        Raises:
            SessionExpiredException: If the requested session has expired.
        """
        session = self._repository.get_or_create(session_id)
        self._check_duration(session)
        return session

    def get_session(self, session_id: str) -> Session:
        """Retrieve a session by ID.

        Args:
            session_id: Unique session identifier.

        Returns:
            The requested session.

        Raises:
            SessionNotFoundException: If the session does not exist.
        """
        session = self._repository.get(session_id)
        if session is None:
            raise SessionNotFoundException(session_id)
        return session

    def add_user_message(
        self,
        session: Session,
        content: str,
        risk_score: int,
        risk_level: RiskLevel,
    ) -> Session:
        """Record a user message with its risk assessment.

        Args:
            session: Active session to update.
            content: User's message text.
            risk_score: Computed risk score (0-100).
            risk_level: Classified risk level.

        Returns:
            The updated session.
        """
        session.add_message(role="user", content=content, risk_score=risk_score)
        session.update_risk(risk_level)
        self._repository.update(session)
        logger.info(
            "User message recorded: session_id=%s, message_count=%d, risk_score=%d",
            session.id,
            session.message_count,
            risk_score,
        )
        return session

    def add_bot_message(self, session: Session, content: str) -> Session:
        """Record a bot response message.

        Args:
            session: Active session to update.
            content: Bot's response text.

        Returns:
            The updated session.
        """
        session.add_message(role="assistant", content=content)
        self._repository.update(session)
        return session

    def mark_triage_activated(self, session: Session) -> Session:
        """Mark a session as having triggered triage.

        Args:
            session: Session to update.

        Returns:
            The updated session.
        """
        session.triage_activated = True
        self._repository.update(session)
        logger.info("Triage activated: session_id=%s", session.id)
        return session

    def mark_handoff(self, session: Session) -> Session:
        """Mark a session as handed off to a professional.

        Args:
            session: Session to update.

        Returns:
            The updated session.
        """
        session.human_handoff = True
        self._repository.update(session)
        logger.info("Handoff initiated: session_id=%s", session.id)
        return session

    def count_active(self) -> int:
        """Count currently active sessions.

        Returns:
            Number of active sessions.
        """
        return self._repository.count_active()

    def _check_duration(self, session: Session) -> None:
        """Verify session has not exceeded maximum duration.

        Args:
            session: Session to check.

        Raises:
            SessionExpiredException: If the session has expired.
        """
        settings = get_settings()
        now = datetime.now(timezone.utc)
        elapsed = (now - session.created_at).total_seconds() / 60.0
        if elapsed > settings.max_session_duration_minutes:
            raise SessionExpiredException(session.id, elapsed)
