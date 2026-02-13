"""Custom exception hierarchy for the clinical chatbot.

Each exception type maps to a specific error scenario with
structured details for logging and client error responses.
"""


class ChatbotBaseException(Exception):
    """Base exception for all chatbot-specific errors.

    Args:
        message: Human-readable error description.
        details: Optional dictionary with additional context for logging.
    """

    def __init__(self, message: str, details: dict | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | details={self.details}"
        return self.message


class SessionNotFoundException(ChatbotBaseException):
    """Raised when a requested session does not exist.

    Args:
        session_id: The ID that was not found.
    """

    def __init__(self, session_id: str) -> None:
        super().__init__(
            message=f"Session not found: {session_id}",
            details={"session_id": session_id},
        )


class SessionExpiredException(ChatbotBaseException):
    """Raised when a session has exceeded its maximum duration.

    Args:
        session_id: The expired session's ID.
        duration_minutes: How long the session has been active.
    """

    def __init__(self, session_id: str, duration_minutes: float) -> None:
        super().__init__(
            message=f"Session expired: {session_id}",
            details={
                "session_id": session_id,
                "duration_minutes": round(duration_minutes, 1),
            },
        )


class InvalidMessageException(ChatbotBaseException):
    """Raised when a user message fails validation.

    Args:
        reason: Description of why the message is invalid.
    """

    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"Invalid message: {reason}",
            details={"reason": reason},
        )


class RiskScoringException(ChatbotBaseException):
    """Raised when risk scoring computation fails.

    Args:
        message: Description of the scoring failure.
        session_id: The session where scoring failed.
    """

    def __init__(self, message: str, session_id: str | None = None) -> None:
        super().__init__(
            message=message,
            details={"session_id": session_id} if session_id else {},
        )


class LLMProviderException(ChatbotBaseException):
    """Raised when the LLM provider encounters an error.

    Args:
        provider: The LLM provider that failed (e.g., 'openai', 'anthropic').
        message: Description of the provider error.
    """

    def __init__(self, provider: str, message: str) -> None:
        super().__init__(
            message=f"LLM provider error ({provider}): {message}",
            details={"provider": provider},
        )


class TriageException(ChatbotBaseException):
    """Raised when triage evaluation encounters an error.

    Args:
        message: Description of the triage failure.
        session_id: The session where triage failed.
    """

    def __init__(self, message: str, session_id: str | None = None) -> None:
        super().__init__(
            message=message,
            details={"session_id": session_id} if session_id else {},
        )
