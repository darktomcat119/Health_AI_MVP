"""Five-signal risk scoring engine.

Computes a risk score (0-100) for each user message by combining:
1. Keyword matching (weighted by severity tier)
2. Negative sentiment word counting
3. Behavioral signals (message length, punctuation, caps)
4. Escalation phrase detection
5. Session history trend analysis

All thresholds are loaded from Settings configuration.
"""

import json
import logging
from pathlib import Path

from app.config import get_settings
from app.exceptions import RiskScoringException
from app.models.enums import RiskLevel
from app.models.session import Session

logger = logging.getLogger(__name__)

# Maximum contribution from each signal
MAX_KEYWORD_SCORE = 30
MAX_SENTIMENT_SCORE = 20
MAX_BEHAVIORAL_SCORE = 20
MAX_ESCALATION_SCORE = 15
MAX_HISTORY_SCORE = 15
MAX_TOTAL_SCORE = 100

# Behavioral signal thresholds
LONG_MESSAGE_THRESHOLD = 300  # characters
PUNCTUATION_THRESHOLD = 3  # exclamation or question marks
CAPS_RATIO_THRESHOLD = 0.30  # 30% uppercase letters

# Behavioral signal point values
LONG_MESSAGE_POINTS = 5
PUNCTUATION_POINTS = 5
CAPS_POINTS = 10

# History thresholds
HIGH_RISK_COUNT_THRESHOLD = 2  # number of high-risk messages
CUMULATIVE_RISK_THRESHOLD = 100  # total risk sum
AVERAGE_RISK_THRESHOLD = 30  # average score over recent messages
MIN_MESSAGES_FOR_AVERAGE = 5  # minimum messages to compute average

# History point values
HIGH_RISK_HISTORY_POINTS = 15
CUMULATIVE_HISTORY_POINTS = 10
AVERAGE_HISTORY_POINTS = 8

# Sentiment analysis word list
NEGATIVE_SENTIMENT_WORDS: list[str] = [
    "terrible", "awful", "worst", "horrible", "miserable",
    "worthless", "useless", "empty", "numb", "broken",
    "crying", "panic", "nightmare", "suffering", "agony",
    "hate", "disgusting", "pathetic", "failure", "stupid",
]

# Points per negative sentiment word found
SENTIMENT_POINTS_PER_WORD = 5

# Escalation phrases indicating acute distress
ESCALATION_PHRASES: list[str] = [
    "i can't anymore",
    "there's no point",
    "what's the use",
    "i'm done",
    "nothing matters",
    "i can't breathe",
    "i give up",
    "no one understands",
]


class RiskScorer:
    """Computes multi-signal risk scores for user messages.

    Loads keyword data from a JSON file and combines five independent
    signals into a composite score capped at 100.
    """

    def __init__(self) -> None:
        self._keywords = self._load_keywords()

    def compute(self, message: str, session: Session) -> int:
        """Compute a risk score (0-100) for a user message.

        Args:
            message: The user's message text.
            session: Current session for history-based scoring.

        Returns:
            Integer risk score between 0 and 100.

        Raises:
            RiskScoringException: If scoring computation fails.
        """
        try:
            lower_message = message.lower()

            keyword_score = self._score_keywords(lower_message)
            sentiment_score = self._score_sentiment(lower_message)
            behavioral_score = self._score_behavioral(message)
            escalation_score = self._score_escalation(lower_message)
            history_score = self._score_history(session)

            total = min(
                keyword_score + sentiment_score + behavioral_score
                + escalation_score + history_score,
                MAX_TOTAL_SCORE,
            )

            logger.debug(
                "Risk signals: keyword=%d, sentiment=%d, behavioral=%d, "
                "escalation=%d, history=%d",
                keyword_score, sentiment_score, behavioral_score,
                escalation_score, history_score,
            )
            logger.info(
                "Risk score computed: session_id=%s, score=%d",
                session.id, total,
            )
            return total

        except Exception as exc:
            raise RiskScoringException(
                message=f"Failed to compute risk score: {exc}",
                session_id=session.id,
            ) from exc

    def classify(self, score: int) -> RiskLevel:
        """Classify a numeric risk score into a risk level.

        Args:
            score: Risk score between 0 and 100.

        Returns:
            RiskLevel classification.
        """
        settings = get_settings()
        if score >= settings.risk_threshold_critical:
            return RiskLevel.CRITICAL
        if score >= settings.risk_threshold_high:
            return RiskLevel.HIGH
        # Medium: 30-59 (below high threshold, above low)
        if score >= 30:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _score_keywords(self, lower_message: str) -> int:
        """Score based on keyword severity tier matches (max 30).

        Takes the HIGHEST matching weight, not cumulative.

        Args:
            lower_message: Lowercased user message.

        Returns:
            Keyword score capped at MAX_KEYWORD_SCORE.
        """
        highest_weight = 0
        for tier_name, tier_data in self._keywords.items():
            weight = tier_data["weight_max"]
            for keyword in tier_data["keywords"]:
                if keyword in lower_message:
                    highest_weight = max(highest_weight, weight)
                    logger.debug(
                        "Keyword match: tier=%s, keyword_found=true, weight=%d",
                        tier_name, weight,
                    )
                    break
        return min(highest_weight, MAX_KEYWORD_SCORE)

    def _score_sentiment(self, lower_message: str) -> int:
        """Score based on negative sentiment word count (max 20).

        Args:
            lower_message: Lowercased user message.

        Returns:
            Sentiment score capped at MAX_SENTIMENT_SCORE.
        """
        count = sum(1 for word in NEGATIVE_SENTIMENT_WORDS if word in lower_message)
        return min(count * SENTIMENT_POINTS_PER_WORD, MAX_SENTIMENT_SCORE)

    def _score_behavioral(self, message: str) -> int:
        """Score based on message behavioral signals (max 20).

        Checks message length, punctuation density, and caps ratio.

        Args:
            message: Original (non-lowercased) user message.

        Returns:
            Behavioral score capped at MAX_BEHAVIORAL_SCORE.
        """
        score = 0

        if len(message) > LONG_MESSAGE_THRESHOLD:
            score += LONG_MESSAGE_POINTS

        exclamation_question_count = message.count("!") + message.count("?")
        if exclamation_question_count >= PUNCTUATION_THRESHOLD:
            score += PUNCTUATION_POINTS

        alpha_chars = [c for c in message if c.isalpha()]
        if alpha_chars:
            upper_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
            if upper_ratio > CAPS_RATIO_THRESHOLD:
                score += CAPS_POINTS

        return min(score, MAX_BEHAVIORAL_SCORE)

    def _score_escalation(self, lower_message: str) -> int:
        """Score based on escalation phrase detection (max 15).

        Any single match triggers the maximum escalation score.

        Args:
            lower_message: Lowercased user message.

        Returns:
            Escalation score: 0 or MAX_ESCALATION_SCORE.
        """
        for phrase in ESCALATION_PHRASES:
            if phrase in lower_message:
                logger.debug("Escalation phrase detected")
                return MAX_ESCALATION_SCORE
        return 0

    def _score_history(self, session: Session) -> int:
        """Score based on session history patterns (max 15).

        Checks for repeated high-risk messages, cumulative risk,
        and average risk over recent messages.

        Args:
            session: Current session with message history.

        Returns:
            History score capped at MAX_HISTORY_SCORE.
        """
        if session.high_risk_count >= HIGH_RISK_COUNT_THRESHOLD:
            return HIGH_RISK_HISTORY_POINTS

        if session.cumulative_risk > CUMULATIVE_RISK_THRESHOLD:
            return CUMULATIVE_HISTORY_POINTS

        if len(session.risk_scores) >= MIN_MESSAGES_FOR_AVERAGE:
            avg = sum(session.risk_scores) / len(session.risk_scores)
            if avg > AVERAGE_RISK_THRESHOLD:
                return AVERAGE_HISTORY_POINTS

        return 0

    def _load_keywords(self) -> dict:
        """Load risk keywords from the configured JSON file.

        Returns:
            Dictionary of keyword tiers with weights and keyword lists.

        Raises:
            RiskScoringException: If the keywords file cannot be loaded.
        """
        settings = get_settings()
        path = Path(settings.risk_keywords_path)
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            raise RiskScoringException(
                message=f"Failed to load risk keywords from {path}: {exc}",
            ) from exc
