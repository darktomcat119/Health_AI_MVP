"""Enumerations for fixed string values used across the application.

All string constants that represent discrete states or categories
are defined here to prevent magic strings and enable type safety.
"""

from enum import Enum


class RiskLevel(str, Enum):
    """Patient risk classification levels.

    Mapped from numeric risk scores (0-100) via RiskScorer.classify().
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MessageRole(str, Enum):
    """Conversation message author roles."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class HandoffReason(str, Enum):
    """Reasons for handing off to a human professional.

    Tracked for clinical audit and quality improvement.
    """

    USER_REQUESTED = "user_requested"
    CRITICAL_RISK = "critical_risk"
    HIGH_RISK = "high_risk"
    MANUAL_TRIGGER = "manual_trigger"


class TriageStatus(str, Enum):
    """Current triage state of a session.

    Progresses from NONE through MONITORING to ACTIVATED or HANDED_OFF.
    """

    NONE = "none"
    MONITORING = "monitoring"
    ACTIVATED = "activated"
    HANDED_OFF = "handed_off"
