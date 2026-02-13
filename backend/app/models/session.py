"""Session dataclass for in-memory conversation state.

Stores conversation history, risk tracking, and triage state
for a single user session. Used by the repository layer.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.models.enums import RiskLevel, TriageStatus


@dataclass
class MessageRecord:
    """Single message stored in a session's history.

    Args:
        role: Message author role (user/assistant/system).
        content: Message text content.
        risk_score: Risk score for user messages, None for bot messages.
        timestamp: UTC timestamp of the message.
    """

    role: str
    content: str
    risk_score: int | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Session:
    """Conversation session holding all state for one user interaction.

    Args:
        id: Unique session identifier.
        messages: Ordered list of messages in this conversation.
        risk_scores: List of risk scores from user messages for trend analysis.
        cumulative_risk: Running sum of all risk scores.
        current_risk_level: Most recent risk classification.
        triage_status: Current triage state.
        triage_activated: Whether triage has been triggered at least once.
        human_handoff: Whether session has been handed off to a professional.
        high_risk_count: Number of messages that scored HIGH or CRITICAL.
        created_at: UTC timestamp when session was created.
        last_activity: UTC timestamp of the most recent message.
    """

    id: str
    messages: list[MessageRecord] = field(default_factory=list)
    risk_scores: list[int] = field(default_factory=list)
    cumulative_risk: int = 0
    current_risk_level: RiskLevel = RiskLevel.LOW
    triage_status: TriageStatus = TriageStatus.NONE
    triage_activated: bool = False
    human_handoff: bool = False
    high_risk_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def message_count(self) -> int:
        """Return total number of messages in this session."""
        return len(self.messages)

    @property
    def duration_minutes(self) -> float:
        """Return session duration in minutes from creation to last activity."""
        delta = self.last_activity - self.created_at
        return delta.total_seconds() / 60.0

    def add_message(self, role: str, content: str, risk_score: int | None = None) -> None:
        """Append a message to the session history and update tracking.

        Args:
            role: Message author role.
            content: Message text.
            risk_score: Risk score for user messages.
        """
        record = MessageRecord(role=role, content=content, risk_score=risk_score)
        self.messages.append(record)
        self.last_activity = datetime.now(timezone.utc)

        if risk_score is not None:
            self.risk_scores.append(risk_score)
            self.cumulative_risk += risk_score

    def update_risk(self, risk_level: RiskLevel) -> None:
        """Update current risk level and track high-risk occurrences.

        Args:
            risk_level: The new risk classification for the session.
        """
        self.current_risk_level = risk_level
        if risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            self.high_risk_count += 1
