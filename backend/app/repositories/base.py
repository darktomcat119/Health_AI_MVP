"""Abstract repository protocol for session storage.

Defines the interface that all session storage implementations must follow.
Uses Python Protocol for structural subtyping (no inheritance required).
"""

from typing import Protocol

from app.models.session import Session


class SessionRepository(Protocol):
    """Protocol defining the session storage interface.

    Implementations must provide all methods defined here.
    Current implementations: InMemorySessionRepository.
    Future: RedisSessionRepository, PostgresSessionRepository.
    """

    def get(self, session_id: str) -> Session | None:
        """Retrieve a session by ID.

        Args:
            session_id: Unique session identifier.

        Returns:
            Session if found and not expired, None otherwise.
        """
        ...

    def create(self, session: Session) -> Session:
        """Store a new session.

        Args:
            session: Session object to persist.

        Returns:
            The persisted session.
        """
        ...

    def update(self, session: Session) -> Session:
        """Update an existing session in storage.

        Args:
            session: Session with updated state.

        Returns:
            The updated session.
        """
        ...

    def delete(self, session_id: str) -> bool:
        """Remove a session from storage.

        Args:
            session_id: ID of the session to remove.

        Returns:
            True if the session was found and deleted, False otherwise.
        """
        ...

    def count_active(self) -> int:
        """Count currently active (non-expired) sessions.

        Returns:
            Number of active sessions.
        """
        ...
