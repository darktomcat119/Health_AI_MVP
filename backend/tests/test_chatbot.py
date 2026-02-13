"""Unit tests for the chatbot service and response validator.

Tests mock response patterns and safety validation rules.
"""

import pytest

from app.services.chatbot import ChatbotService, ResponseValidator

from tests.conftest import create_session


class TestChatbotMockResponses:
    """Tests for ChatbotService mock response patterns."""

    @pytest.mark.asyncio
    async def test_greeting_returns_warm_response(self, chatbot_service: ChatbotService) -> None:
        """Greetings should produce a warm welcome."""
        session = create_session()
        response = await chatbot_service.generate_response("Hello!", session)
        assert "welcome" in response.lower() or "glad" in response.lower()

    @pytest.mark.asyncio
    async def test_stress_returns_empathetic_response(self, chatbot_service: ChatbotService) -> None:
        """Stress-related messages should get empathetic responses."""
        session = create_session()
        response = await chatbot_service.generate_response(
            "I've been really stressed out lately", session,
        )
        assert "stress" in response.lower() or "pressure" in response.lower()

    @pytest.mark.asyncio
    async def test_farewell_returns_closing(self, chatbot_service: ChatbotService) -> None:
        """Farewell messages should get a warm closing."""
        session = create_session()
        response = await chatbot_service.generate_response("Goodbye, take care", session)
        assert "care" in response.lower() or "welcome" in response.lower()

    @pytest.mark.asyncio
    async def test_default_response_is_empathetic(self, chatbot_service: ChatbotService) -> None:
        """Unmatched messages should get an empathetic open question."""
        session = create_session()
        response = await chatbot_service.generate_response(
            "The weather is interesting today", session,
        )
        assert "listen" in response.lower() or "sharing" in response.lower()

    @pytest.mark.asyncio
    async def test_returning_user_gets_different_greeting(
        self, chatbot_service: ChatbotService,
    ) -> None:
        """Returning users should get a different greeting."""
        session = create_session(messages=4)
        response = await chatbot_service.generate_response("Hello again", session)
        assert "back" in response.lower() or "again" in response.lower()

    @pytest.mark.asyncio
    async def test_sleep_issue_response(self, chatbot_service: ChatbotService) -> None:
        """Sleep-related messages should get sleep-specific response."""
        session = create_session()
        response = await chatbot_service.generate_response(
            "I can't sleep at night", session,
        )
        assert "sleep" in response.lower()


class TestResponseValidator:
    """Tests for ResponseValidator safety checks."""

    def test_blocks_diagnosis_language(self) -> None:
        """Diagnostic language should be blocked."""
        validator = ResponseValidator()
        result = validator.validate("Based on what you've said, you have depression.")
        assert result == validator.SAFE_FALLBACK

    def test_blocks_medication_advice(self) -> None:
        """Medication recommendations should be blocked."""
        validator = ResponseValidator()
        result = validator.validate("You should take some anxiety medication.")
        assert result == validator.SAFE_FALLBACK

    def test_blocks_minimizing_language(self) -> None:
        """Minimizing language should be blocked."""
        validator = ResponseValidator()
        result = validator.validate("Just calm down, it's not that bad.")
        assert result == validator.SAFE_FALLBACK

    def test_passes_safe_response(self) -> None:
        """Safe empathetic responses should pass through unchanged."""
        validator = ResponseValidator()
        safe_response = "I hear you. Can you tell me more about how you're feeling?"
        result = validator.validate(safe_response)
        assert result == safe_response
