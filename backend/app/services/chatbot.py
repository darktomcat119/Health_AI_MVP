"""LLM orchestrator and response validation service.

Manages the full pipeline from user message to validated bot response:
1. Anonymize PII from the message
2. Send to LLM provider (mock or API-based)
3. Validate response against safety rules
4. Return safe, validated response

The mock provider ships pattern-matched responses for development
without requiring any external API keys.
"""

import asyncio
import logging
import re
from collections.abc import AsyncGenerator

from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError

from app.config import get_settings
from app.exceptions import LLMProviderException
from app.models.session import Session
from app.services.anonymizer import Anonymizer

logger = logging.getLogger(__name__)

# Number of conversation turns to include as context for the LLM
MAX_CONTEXT_MESSAGES = 10

SYSTEM_PROMPT = (
    "You are a compassionate, empathetic mental health support chatbot. "
    "You are NOT a licensed therapist or medical professional. "
    "Your role is to listen actively, validate feelings, and provide emotional support.\n\n"
    "Guidelines:\n"
    "- Never diagnose conditions or recommend medication\n"
    "- Never minimize feelings or tell users to 'just calm down'\n"
    "- Use empathetic, validating language\n"
    "- Ask open-ended questions to understand the user better\n"
    "- If someone is in crisis, encourage them to contact emergency services or a crisis hotline\n"
    "- Keep responses concise but warm (2-4 sentences)\n"
    "- Respond in the same language the user writes in\n"
    "- User messages may contain privacy placeholders like [NAME], [EMAIL], [PHONE], or [ADDRESS]. "
    "Never repeat these placeholders in your response. Simply skip over them naturally "
    "and do not ask the user for their personal information."
)


class ResponseValidator:
    """Validates bot responses against clinical safety rules.

    Blocks responses that contain diagnostic language, medication
    recommendations, or minimizing phrases. Replaces blocked
    responses with a safe fallback.
    """

    BLOCKED_PATTERNS: dict[str, list[str]] = {
        "diagnosis": [
            "you have",
            "you are diagnosed",
            "you suffer from",
            "your condition is",
            "you might have",
        ],
        "medication": [
            "you should take",
            "try taking",
            "medication",
            "prescription",
            "dosage",
            " mg ",
            "pills",
        ],
        "minimizing": [
            "just calm down",
            "it's not that bad",
            "you're overreacting",
            "just relax",
            "get over it",
            "cheer up",
            "think positive",
        ],
    }

    SAFE_FALLBACK = (
        "I want to make sure I support you well. Could you tell me "
        "a bit more about how you're feeling? I'm here to listen."
    )

    def validate(self, response: str) -> str:
        """Check a response for blocked patterns and return safe output.

        Args:
            response: The raw LLM response text.

        Returns:
            The original response if safe, or SAFE_FALLBACK if blocked.
        """
        lower_response = response.lower()
        for category, patterns in self.BLOCKED_PATTERNS.items():
            for pattern in patterns:
                if pattern in lower_response:
                    logger.warning(
                        "Response blocked: category=%s, pattern_matched=true",
                        category,
                    )
                    return self.SAFE_FALLBACK
        return response


class ChatbotService:
    """Orchestrates the full chat response pipeline.

    Coordinates anonymization, LLM invocation, and response validation
    to produce safe, empathetic responses.

    Args:
        anonymizer: PII stripping service.
        validator: Response safety validator.
    """

    def __init__(
        self,
        anonymizer: Anonymizer | None = None,
        validator: ResponseValidator | None = None,
    ) -> None:
        self._anonymizer = anonymizer or Anonymizer()
        self._validator = validator or ResponseValidator()

    async def generate_response(self, message: str, session: Session) -> str:
        """Process a user message through the full pipeline.

        Args:
            message: Raw user message.
            session: Current conversation session.

        Returns:
            Validated bot response text.
        """
        anonymized = self._anonymizer.anonymize(message)
        raw_response = await self._get_llm_response(anonymized, session)
        validated = self._validator.validate(raw_response)
        return validated

    async def _get_llm_response(self, message: str, session: Session) -> str:
        """Route to the configured LLM provider.

        Args:
            message: Anonymized user message.
            session: Current session for context.

        Returns:
            Raw LLM response text.

        Raises:
            LLMProviderException: If the provider is not supported.
        """
        settings = get_settings()
        if settings.llm_provider == "mock":
            return self._mock_response(message, session)
        if settings.llm_provider == "openai":
            return await self._openai_response(message, session)

        raise LLMProviderException(
            provider=settings.llm_provider,
            message=f"Provider '{settings.llm_provider}' is not implemented. "
            f"Use 'mock' for development.",
        )

    async def _openai_response(self, message: str, session: Session) -> str:
        """Call the OpenAI API with conversation context.

        Args:
            message: Anonymized user message.
            session: Current session for conversation history.

        Returns:
            Raw LLM response text.

        Raises:
            LLMProviderException: On API errors.
        """
        settings = get_settings()
        client = AsyncOpenAI(api_key=settings.llm_api_key)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        recent = session.messages[-MAX_CONTEXT_MESSAGES:]
        for msg in recent:
            role = "assistant" if msg.role == "assistant" else "user"
            messages.append({"role": role, "content": msg.content})

        messages.append({"role": "user", "content": message})

        try:
            params = {
                "model": settings.llm_model,
                "messages": messages,
                "max_completion_tokens": settings.llm_max_tokens,
            }
            if settings.llm_temperature is not None:
                params["temperature"] = settings.llm_temperature

            response = await client.chat.completions.create(**params)
            choice = response.choices[0]
            content = choice.message.content or ""
            logger.info(
                "OpenAI response: finish_reason=%s, content_length=%d",
                choice.finish_reason, len(content),
            )
            if not content:
                logger.warning("OpenAI returned empty content: %s", choice.message)
            return content
        except RateLimitError as exc:
            raise LLMProviderException(
                provider="openai", message="Rate limit exceeded. Please try again later."
            ) from exc
        except APIConnectionError as exc:
            raise LLMProviderException(
                provider="openai", message="Could not connect to OpenAI API."
            ) from exc
        except APIError as exc:
            raise LLMProviderException(
                provider="openai", message=str(exc)
            ) from exc

    async def stream_response(
        self, message: str, session: Session
    ) -> AsyncGenerator[str, None]:
        """Stream tokens from the LLM, yielding each as it arrives.

        After all tokens are yielded, validates the full response.
        If validation replaces the response, yields a special sentinel
        so the caller can send a 'replace' SSE event.

        Yields:
            Individual tokens from the LLM, or a replacement sentinel
            in the format ``__REPLACE__:<safe_text>`` if validation fails.
        """
        anonymized = self._anonymizer.anonymize(message)
        settings = get_settings()

        if settings.llm_provider == "openai":
            full_text = ""
            async for token in self._openai_stream(anonymized, session):
                full_text += token
                yield token

            validated = self._validator.validate(full_text)
            if validated != full_text:
                yield f"__REPLACE__{validated}"
        else:
            # Mock and other providers: fall back to non-streaming
            response = await self._get_llm_response(anonymized, session)
            validated = self._validator.validate(response)
            yield validated

    async def _openai_stream(
        self, message: str, session: Session
    ) -> AsyncGenerator[str, None]:
        """Stream tokens from the OpenAI API.

        Args:
            message: Anonymized user message.
            session: Current session for conversation history.

        Yields:
            Individual content tokens from the model.
        """
        settings = get_settings()
        client = AsyncOpenAI(api_key=settings.llm_api_key)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        recent = session.messages[-MAX_CONTEXT_MESSAGES:]
        for msg in recent:
            role = "assistant" if msg.role == "assistant" else "user"
            messages.append({"role": role, "content": msg.content})

        messages.append({"role": "user", "content": message})

        try:
            params = {
                "model": settings.llm_model,
                "messages": messages,
                "max_completion_tokens": settings.llm_max_tokens,
                "stream": True,
            }
            if settings.llm_temperature is not None:
                params["temperature"] = settings.llm_temperature

            stream = await client.chat.completions.create(**params)
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except (RateLimitError, APIConnectionError, APIError) as exc:
            raise LLMProviderException(
                provider="openai", message=str(exc)
            ) from exc

    def _mock_response(self, message: str, session: Session) -> str:
        """Generate a pattern-matched mock response for development.

        Uses keyword detection to select contextually appropriate
        empathetic responses without requiring an external LLM.

        Args:
            message: Anonymized user message.
            session: Current session for context awareness.

        Returns:
            Mock bot response text.
        """
        lower = message.lower()

        if self._matches_farewell(lower):
            return self._response_farewell()
        if self._matches_greeting(lower):
            return self._response_greeting(session)
        if self._matches_sleep(lower):
            return self._response_sleep()
        if self._matches_stress(lower):
            return self._response_stress()
        if self._matches_sadness(lower):
            return self._response_sadness()
        if self._matches_relationship(lower):
            return self._response_relationship()
        if self._matches_work_school(lower):
            return self._response_work_school()
        if self._matches_positive(lower):
            return self._response_positive()
        return self._response_default()

    def _matches_greeting(self, text: str) -> bool:
        """Check if message is a greeting."""
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "hola", "buenos"]
        return any(g in text for g in greetings)

    def _matches_stress(self, text: str) -> bool:
        """Check if message mentions stress or anxiety."""
        keywords = ["stress", "anxious", "anxiety", "worried", "nervous", "tense", "overwhelmed"]
        return any(k in text for k in keywords)

    def _matches_sadness(self, text: str) -> bool:
        """Check if message mentions sadness or depression."""
        keywords = ["sad", "depressed", "depression", "down", "unhappy", "crying", "tears"]
        return any(k in text for k in keywords)

    def _matches_positive(self, text: str) -> bool:
        """Check if message is positive."""
        keywords = ["better", "good", "great", "happy", "improved", "progress", "grateful"]
        return any(k in text for k in keywords)

    def _matches_sleep(self, text: str) -> bool:
        """Check if message mentions sleep issues."""
        keywords = ["sleep", "insomnia", "can't sleep", "nightmares", "tired", "exhausted"]
        return any(k in text for k in keywords)

    def _matches_relationship(self, text: str) -> bool:
        """Check if message mentions relationships."""
        keywords = ["relationship", "partner", "family", "friend", "lonely", "breakup", "divorce"]
        return any(k in text for k in keywords)

    def _matches_work_school(self, text: str) -> bool:
        """Check if message mentions work or school."""
        keywords = ["work", "job", "school", "college", "boss", "coworker", "grades", "career"]
        return any(k in text for k in keywords)

    def _matches_farewell(self, text: str) -> bool:
        """Check if message is a farewell."""
        keywords = ["bye", "goodbye", "see you", "take care", "gotta go", "talk later"]
        return any(k in text for k in keywords)

    def _response_greeting(self, session: Session) -> str:
        """Return warm welcome response."""
        if session.message_count == 0:
            return (
                "Hello! Welcome \u2014 I'm really glad you're here. "
                "This is a safe space where you can share whatever is on your mind. "
                "There's no rush and no judgment. How are you feeling today?"
            )
        return (
            "Welcome back! It's good to hear from you again. "
            "How have things been since we last talked?"
        )

    def _response_stress(self) -> str:
        """Return empathetic stress acknowledgment."""
        return (
            "I hear you \u2014 it sounds like you've been carrying a lot of weight. "
            "Stress can really take a toll on us, both mentally and physically. "
            "Can you tell me a bit more about what's been causing the most pressure? "
            "Sometimes just naming it can help lighten the load a little."
        )

    def _response_sadness(self) -> str:
        """Return validating sadness response."""
        return (
            "Thank you for sharing that with me. Feeling sad is a completely valid "
            "emotion, and it takes courage to acknowledge it. I want you to know that "
            "what you're feeling matters. How long have you been feeling this way? "
            "Understanding the timeline can help us figure out the best way to support you."
        )

    def _response_positive(self) -> str:
        """Return reinforcing positive response."""
        return (
            "That's really wonderful to hear! It's so important to recognize and "
            "celebrate the positive moments, no matter how small they might seem. "
            "What do you think has been contributing to this improvement? "
            "I'd also love to check in \u2014 is there anything else on your mind?"
        )

    def _response_sleep(self) -> str:
        """Return sleep-focused acknowledgment."""
        return (
            "Sleep is so fundamental to how we feel during the day, and I'm sorry "
            "that rest hasn't been coming easily. Poor sleep can amplify everything else "
            "we're dealing with. Can you tell me more about what your nights look like? "
            "For example, is the difficulty with falling asleep, staying asleep, or both?"
        )

    def _response_relationship(self) -> str:
        """Return relationship-empathetic response."""
        return (
            "Relationships are such an important part of our lives, and when they're "
            "difficult, it can affect everything else. I appreciate you trusting me "
            "with this. Can you share a bit more about what's been happening? "
            "I'm here to listen without judgment."
        )

    def _response_work_school(self) -> str:
        """Return work/school normalizing response."""
        return (
            "Work and school pressures are something so many people struggle with, "
            "and it's completely understandable to feel the weight of it. You're not "
            "alone in this. What aspect has been the most challenging for you lately? "
            "Let's see if we can break it down together."
        )

    def _response_farewell(self) -> str:
        """Return warm closing response."""
        return (
            "Thank you for spending this time with me today. I want you to know that "
            "you're always welcome to come back whenever you need to talk. "
            "Remember to be kind to yourself \u2014 you deserve it. Take care, "
            "and don't hesitate to reach out anytime."
        )

    def _response_default(self) -> str:
        """Return empathetic open question for unmatched messages."""
        return (
            "Thank you for sharing that with me. I want to make sure I understand "
            "you well. Could you tell me a bit more about what's been on your mind? "
            "I'm here to listen, and there's no wrong thing to say."
        )
