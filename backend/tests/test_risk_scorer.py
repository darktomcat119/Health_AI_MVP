"""Unit tests for the risk scoring engine.

Tests all five risk signals and the classification boundaries.
"""

import pytest

from app.models.enums import RiskLevel
from app.models.session import Session
from app.services.risk_scorer import RiskScorer

from tests.conftest import create_session


class TestRiskScorerCompute:
    """Tests for RiskScorer.compute()."""

    def test_greeting_scores_low(self, risk_scorer: RiskScorer) -> None:
        """A simple greeting should produce a low score."""
        session = create_session()
        score = risk_scorer.compute("Hello, how are you?", session)
        assert score < 30

    def test_sadness_detected(self, risk_scorer: RiskScorer) -> None:
        """Sadness keywords should produce a moderate score."""
        session = create_session()
        score = risk_scorer.compute("I feel really sad and lonely today", session)
        assert score >= 5

    def test_critical_keyword_high_score(self, risk_scorer: RiskScorer) -> None:
        """Critical keywords should produce a high score."""
        session = create_session()
        score = risk_scorer.compute("I want to kill myself", session)
        assert score >= 25

    def test_sentiment_words_increase_score(self, risk_scorer: RiskScorer) -> None:
        """Multiple negative sentiment words should increase the score."""
        session = create_session()
        score = risk_scorer.compute(
            "Everything is terrible and awful, I feel miserable and worthless",
            session,
        )
        assert score >= 15

    def test_caps_behavioral_signal(self, risk_scorer: RiskScorer) -> None:
        """Messages in ALL CAPS should trigger behavioral scoring."""
        session = create_session()
        score_normal = risk_scorer.compute("I need help please", session)
        score_caps = risk_scorer.compute("I NEED HELP PLEASE NOW", session)
        assert score_caps > score_normal

    def test_long_message_behavioral_signal(self, risk_scorer: RiskScorer) -> None:
        """Long messages should trigger behavioral scoring."""
        session = create_session()
        short_msg = "I feel bad"
        long_msg = "I feel bad " * 50  # well over 300 chars
        score_short = risk_scorer.compute(short_msg, session)
        score_long = risk_scorer.compute(long_msg, session)
        assert score_long > score_short

    def test_escalation_phrase_detected(self, risk_scorer: RiskScorer) -> None:
        """Escalation phrases should add 15 points."""
        session = create_session()
        score = risk_scorer.compute("i can't anymore, nothing matters", session)
        assert score >= 15

    def test_session_history_boost(self, risk_scorer: RiskScorer, high_risk_session: Session) -> None:
        """Sessions with high-risk history should get a history boost."""
        score = risk_scorer.compute("I still feel the same way", high_risk_session)
        # History should contribute since high_risk_count >= 2
        assert score >= 15

    def test_score_never_exceeds_100(self, risk_scorer: RiskScorer) -> None:
        """Even extreme messages should cap at 100."""
        session = create_session()
        session.high_risk_count = 5
        session.cumulative_risk = 500
        score = risk_scorer.compute(
            "I WANT TO KILL MYSELF!!! I CAN'T ANYMORE!!! "
            "TERRIBLE AWFUL HORRIBLE MISERABLE WORTHLESS PATHETIC",
            session,
        )
        assert score <= 100


class TestRiskScorerClassify:
    """Tests for RiskScorer.classify()."""

    @pytest.mark.parametrize(
        ("score", "expected_level"),
        [
            (0, RiskLevel.LOW),
            (15, RiskLevel.LOW),
            (29, RiskLevel.LOW),
            (30, RiskLevel.MEDIUM),
            (45, RiskLevel.MEDIUM),
            (59, RiskLevel.MEDIUM),
            (60, RiskLevel.HIGH),
            (70, RiskLevel.HIGH),
            (79, RiskLevel.HIGH),
            (80, RiskLevel.CRITICAL),
            (90, RiskLevel.CRITICAL),
            (100, RiskLevel.CRITICAL),
        ],
    )
    def test_classify_boundaries(
        self, risk_scorer: RiskScorer, score: int, expected_level: RiskLevel,
    ) -> None:
        """Classification should match the expected boundaries."""
        assert risk_scorer.classify(score) == expected_level
