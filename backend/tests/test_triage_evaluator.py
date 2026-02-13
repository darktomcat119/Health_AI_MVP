"""Unit tests for the triage evaluation engine.

Tests all four triage rules and their priority ordering.
"""

import pytest

from app.models.enums import HandoffReason, RiskLevel
from app.services.triage_evaluator import TriageEvaluator

from tests.conftest import create_session


class TestTriageEvaluator:
    """Tests for TriageEvaluator.evaluate()."""

    def test_no_triage_on_low_risk(self, triage_evaluator: TriageEvaluator) -> None:
        """Low-risk messages should not trigger triage."""
        session = create_session()
        result = triage_evaluator.evaluate("I had a good day", 10, RiskLevel.LOW, session)
        assert result.triage_activated is False
        assert result.human_handoff is False
        assert result.override_response is None

    def test_high_risk_triggers_handoff(self, triage_evaluator: TriageEvaluator) -> None:
        """High-risk scores should trigger triage and handoff."""
        session = create_session()
        result = triage_evaluator.evaluate("I feel hopeless", 65, RiskLevel.HIGH, session)
        assert result.triage_activated is True
        assert result.human_handoff is True
        assert result.handoff_reason == HandoffReason.HIGH_RISK

    def test_critical_includes_crisis_resources(self, triage_evaluator: TriageEvaluator) -> None:
        """Critical risk should include crisis resources."""
        session = create_session()
        result = triage_evaluator.evaluate("I want to end my life", 85, RiskLevel.CRITICAL, session)
        assert result.triage_activated is True
        assert result.human_handoff is True
        assert len(result.crisis_resources) > 0
        assert result.handoff_reason == HandoffReason.CRITICAL_RISK

    def test_critical_response_contains_phone_numbers(
        self, triage_evaluator: TriageEvaluator,
    ) -> None:
        """Critical triage response should include emergency phone numbers."""
        session = create_session()
        result = triage_evaluator.evaluate("I want to die", 85, RiskLevel.CRITICAL, session)
        assert "800-911-2000" in result.override_response
        assert "55 5259-8121" in result.override_response
        assert "911" in result.override_response

    def test_user_requests_human_english(self, triage_evaluator: TriageEvaluator) -> None:
        """English human request phrases should trigger handoff."""
        session = create_session()
        result = triage_evaluator.evaluate(
            "I want to talk to a real person", 10, RiskLevel.LOW, session,
        )
        assert result.triage_activated is True
        assert result.human_handoff is True
        assert result.handoff_reason == HandoffReason.USER_REQUESTED

    def test_user_requests_human_spanish(self, triage_evaluator: TriageEvaluator) -> None:
        """Spanish human request phrases should trigger handoff."""
        session = create_session()
        result = triage_evaluator.evaluate(
            "Necesito hablar con alguien", 10, RiskLevel.LOW, session,
        )
        assert result.triage_activated is True
        assert result.human_handoff is True
        assert result.handoff_reason == HandoffReason.USER_REQUESTED

    def test_long_session_triggers_checkin(self, triage_evaluator: TriageEvaluator) -> None:
        """Sessions exceeding message threshold should get a check-in."""
        session = create_session(messages=16)
        result = triage_evaluator.evaluate("Tell me more", 10, RiskLevel.LOW, session)
        assert result.override_response is not None
        assert "check in" in result.override_response.lower()
        assert result.human_handoff is False

    def test_user_request_takes_priority_over_score(
        self, triage_evaluator: TriageEvaluator,
    ) -> None:
        """User requesting human should take priority over high risk score."""
        session = create_session()
        result = triage_evaluator.evaluate(
            "I need help now, talk to a real person", 85, RiskLevel.CRITICAL, session,
        )
        assert result.handoff_reason == HandoffReason.USER_REQUESTED

    def test_long_session_no_trigger_if_already_triaged(
        self, triage_evaluator: TriageEvaluator,
    ) -> None:
        """Long session check-in should not trigger if triage already activated."""
        session = create_session(messages=16)
        session.triage_activated = True
        result = triage_evaluator.evaluate("Tell me more", 10, RiskLevel.LOW, session)
        assert result.triage_activated is False
        assert result.override_response is None
