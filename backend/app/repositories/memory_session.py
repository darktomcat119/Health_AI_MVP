"""Thread-safe in-memory session repository.

Stores sessions in a dictionary protected by threading.Lock.
Implements automatic expiry checking on read operations.
Suitable for development and single-instance deployments.
"""

import logging
import threading
import uuid
from datetime import datetime, timezone

from app.config import get_settings
from app.models.session import Session

logger = logging.getLogger(__name__)


class InMemorySessionRepository:
    """In-memory session store with thread-safe access.

    Uses threading.Lock to ensure safe concurrent reads and writes.
    Expired sessions are detected on access and automatically removed.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = threading.Lock()

    def get(self, session_id: str) -> Session | None:
        """Retrieve a session by ID, returning None if expired or missing.

        Args:
            session_id: Unique session identifier.

        Returns:
            Session if found and not expired, None otherwise.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None

            if self._is_expired(session):
                logger.info("Session expired, removing: session_id=%s", session_id)
                del self._sessions[session_id]
                return None

            return session

    def create(self, session: Session) -> Session:
        """Store a new session.

        Args:
            session: Session object to persist.

        Returns:
            The persisted session.
        """
        with self._lock:
            self._sessions[session.id] = session
            logger.info("Session created: session_id=%s", session.id)
            return session

    def update(self, session: Session) -> Session:
        """Update an existing session in storage.

        Args:
            session: Session with updated state.

        Returns:
            The updated session.
        """
        with self._lock:
            self._sessions[session.id] = session
            return session

    def delete(self, session_id: str) -> bool:
        """Remove a session from storage.

        Args:
            session_id: ID of the session to remove.

        Returns:
            True if the session was found and deleted, False otherwise.
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                logger.info("Session deleted: session_id=%s", session_id)
                return True
            return False

    def count_active(self) -> int:
        """Count currently active (non-expired) sessions.

        Returns:
            Number of active sessions.
        """
        with self._lock:
            self._cleanup_expired()
            return len(self._sessions)

    def get_or_create(self, session_id: str | None) -> Session:
        """Retrieve an existing session or create a new one.

        Args:
            session_id: Existing session ID, or None to create a new session.

        Returns:
            The existing or newly created session.
        """
        if session_id:
            session = self.get(session_id)
            if session is not None:
                return session

        new_id = f"sess_{uuid.uuid4().hex[:12]}"
        new_session = Session(id=new_id)
        return self.create(new_session)

    def _is_expired(self, session: Session) -> bool:
        """Check if a session has exceeded the maximum duration.

        Args:
            session: Session to check.

        Returns:
            True if the session has expired.
        """
        settings = get_settings()
        now = datetime.now(timezone.utc)
        elapsed = (now - session.created_at).total_seconds() / 60.0
        return elapsed > settings.max_session_duration_minutes

    def _cleanup_expired(self) -> None:
        """Remove all expired sessions from storage. Must be called within lock."""
        expired_ids = [
            sid for sid, session in self._sessions.items()
            if self._is_expired(session)
        ]
        for sid in expired_ids:
            del self._sessions[sid]
            logger.info("Expired session cleaned up: session_id=%s", sid)
