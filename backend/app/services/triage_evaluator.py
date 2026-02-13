"""Triage evaluation engine with cascading rule system.

Evaluates each message against four ordered rules to determine
whether triage should activate, a professional handoff is needed,
and what crisis resources to provide.

Rules are evaluated in strict order — first match wins.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from app.config import get_settings
from app.exceptions import TriageException
from app.models.enums import HandoffReason, RiskLevel
from app.models.schemas import CrisisResource
from app.models.session import Session

logger = logging.getLogger(__name__)

# Phrases indicating the user wants to speak with a human
HUMAN_REQUEST_PHRASES: list[str] = [
    "talk to a person",
    "real person",
    "talk to someone",
    "speak to a human",
    "want a therapist",
    "need a professional",
    "talk to a doctor",
    "need help now",
    "speak to someone real",
    "hablar con alguien",
    "necesito hablar con alguien",
]

# Pre-written response templates for each triage scenario
RESPONSE_USER_REQUESTED = (
    "Of course. I'm connecting you with a professional right now. "
    "They will have the context of our conversation so you don't have "
    "to repeat anything. Please stay with me while I connect you."
)

RESPONSE_CRITICAL = (
    "I hear you, and what you're feeling matters. I want to make sure "
    "you get the right support right now. I'm connecting you with a "
    "professional immediately.\n\n"
    "If you need to talk to someone right now, these lines are available 24/7:\n"
    "\u2022 Linea de la Vida: 800-911-2000 (free, national)\n"
    "\u2022 SAPTEL: 55 5259-8121\n"
    "\u2022 Emergency: 911\n\n"
    "A professional is being notified right now. Please stay here."
)

RESPONSE_HIGH_RISK = (
    "Thank you for sharing that with me. I think it would be really helpful "
    "for you to talk with one of our professionals. I'm going to connect you "
    "now \u2014 they'll be able to see our conversation so you can continue "
    "from where we are."
)

RESPONSE_LONG_SESSION = (
    "We've been talking for a while, and I want to check in with you. "
    "How are you feeling right now? If you'd like to talk to a professional "
    "at any point, just let me know."
)


@dataclass
class TriageResult:
    """Result of triage evaluation for a single message.

    Args:
        triage_activated: Whether triage was triggered.
        human_handoff: Whether a professional handoff is initiated.
        crisis_resources: List of crisis resources to show (if any).
        override_response: Pre-written response that overrides the LLM output.
        handoff_reason: Reason for handoff (if applicable).
    """

    triage_activated: bool = False
    human_handoff: bool = False
    crisis_resources: list[CrisisResource] = field(default_factory=list)
    override_response: str | None = None
    handoff_reason: HandoffReason | None = None


class TriageEvaluator:
    """Evaluates messages against triage rules in priority order.

    Rules are checked sequentially; the first matching rule determines
    the triage outcome. This ensures deterministic, auditable behavior.
    """

    def __init__(self) -> None:
        self._crisis_resources = self._load_crisis_resources()

    def evaluate(
        self,
        message: str,
        risk_score: int,
        risk_level: RiskLevel,
        session: Session,
    ) -> TriageResult:
        """Evaluate a message against all triage rules.

        Args:
            message: The user's message text.
            risk_score: Computed risk score (0-100).
            risk_level: Classified risk level.
            session: Current session state.

        Returns:
            TriageResult with the evaluation outcome.

        Raises:
            TriageException: If evaluation fails.
        """
        try:
            result = self._check_user_requests_human(message)
            if result is not None:
                logger.info(
                    "Triage rule matched: user_requested, session_id=%s",
                    session.id,
                )
                return result

            result = self._check_critical_risk(risk_score, risk_level)
            if result is not None:
                logger.info(
                    "Triage rule matched: critical_risk, session_id=%s, score=%d",
                    session.id, risk_score,
                )
                return result

            result = self._check_high_risk(risk_score, risk_level)
            if result is not None:
                logger.info(
                    "Triage rule matched: high_risk, session_id=%s, score=%d",
                    session.id, risk_score,
                )
                return result

            result = self._check_long_session(session)
            if result is not None:
                logger.info(
                    "Triage rule matched: long_session, session_id=%s, count=%d",
                    session.id, session.message_count,
                )
                return result

            logger.info(
                "No triage triggered: session_id=%s, score=%d, level=%s",
                session.id, risk_score, risk_level.value,
            )
            return TriageResult()

        except Exception as exc:
            raise TriageException(
                message=f"Triage evaluation failed: {exc}",
                session_id=session.id,
            ) from exc

    def _check_user_requests_human(self, message: str) -> TriageResult | None:
        """Rule 1: User explicitly requests to speak with a human.

        Args:
            message: User's message text.

        Returns:
            TriageResult if matched, None otherwise.
        """
        lower_message = message.lower()
        for phrase in HUMAN_REQUEST_PHRASES:
            if phrase in lower_message:
                return TriageResult(
                    triage_activated=True,
                    human_handoff=True,
                    override_response=RESPONSE_USER_REQUESTED,
                    handoff_reason=HandoffReason.USER_REQUESTED,
                )
        return None

    def _check_critical_risk(
        self, risk_score: int, risk_level: RiskLevel,
    ) -> TriageResult | None:
        """Rule 2: Risk score is at critical level.

        Args:
            risk_score: Computed risk score.
            risk_level: Classified risk level.

        Returns:
            TriageResult if matched, None otherwise.
        """
        settings = get_settings()
        if risk_score >= settings.risk_threshold_critical:
            return TriageResult(
                triage_activated=True,
                human_handoff=True,
                crisis_resources=self._crisis_resources,
                override_response=RESPONSE_CRITICAL,
                handoff_reason=HandoffReason.CRITICAL_RISK,
            )
        return None

    def _check_high_risk(
        self, risk_score: int, risk_level: RiskLevel,
    ) -> TriageResult | None:
        """Rule 3: Risk score is at high level.

        Args:
            risk_score: Computed risk score.
            risk_level: Classified risk level.

        Returns:
            TriageResult if matched, None otherwise.
        """
        settings = get_settings()
        if risk_score >= settings.risk_threshold_high:
            return TriageResult(
                triage_activated=True,
                human_handoff=True,
                override_response=RESPONSE_HIGH_RISK,
                handoff_reason=HandoffReason.HIGH_RISK,
            )
        return None

    def _check_long_session(self, session: Session) -> TriageResult | None:
        """Rule 4: Session has exceeded the message check-in threshold.

        Only triggers if triage has not already been activated.

        Args:
            session: Current session state.

        Returns:
            TriageResult if matched, None otherwise.
        """
        settings = get_settings()
        if (
            session.message_count >= settings.session_max_messages_before_checkin
            and not session.triage_activated
        ):
            return TriageResult(
                triage_activated=False,
                human_handoff=False,
                override_response=RESPONSE_LONG_SESSION,
            )
        return None

    def _load_crisis_resources(self) -> list[CrisisResource]:
        """Load crisis resources from the configured JSON file.

        Returns:
            List of CrisisResource objects.

        Raises:
            TriageException: If the resources file cannot be loaded.
        """
        settings = get_settings()
        path = Path(settings.crisis_resources_path)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return [CrisisResource(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            raise TriageException(
                message=f"Failed to load crisis resources from {path}: {exc}",
            ) from exc
