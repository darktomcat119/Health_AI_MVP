"""Unit tests for the PII anonymizer.

Tests all PII pattern detection and replacement.
"""

from app.services.anonymizer import Anonymizer


class TestAnonymizer:
    """Tests for Anonymizer.anonymize()."""

    def setup_method(self) -> None:
        """Create a fresh anonymizer for each test."""
        self.anonymizer = Anonymizer()

    def test_masks_email_address(self) -> None:
        """Email addresses should be replaced with [EMAIL]."""
        text = "Contact me at juan.garcia@example.com please"
        result = self.anonymizer.anonymize(text)
        assert "[EMAIL]" in result
        assert "juan.garcia@example.com" not in result

    def test_masks_mexican_phone_number(self) -> None:
        """Mexican phone numbers should be replaced with [PHONE]."""
        text = "My number is 55 1234-5678"
        result = self.anonymizer.anonymize(text)
        assert "[PHONE]" in result
        assert "1234-5678" not in result

    def test_masks_name_after_my_name_is(self) -> None:
        """Names after 'my name is' should be replaced with [NAME]."""
        text = "Hi, my name is Carlos Garcia and I need help"
        result = self.anonymizer.anonymize(text)
        assert "[NAME]" in result
        assert "Carlos Garcia" not in result

    def test_masks_name_after_me_llamo(self) -> None:
        """Names after 'me llamo' should be replaced with [NAME]."""
        text = "Hola, me llamo Maria Lopez"
        result = self.anonymizer.anonymize(text)
        assert "[NAME]" in result
        assert "Maria Lopez" not in result

    def test_preserves_normal_text(self) -> None:
        """Text without PII should pass through unchanged."""
        text = "I have been feeling stressed about work lately"
        result = self.anonymizer.anonymize(text)
        assert result == text

    def test_masks_ten_digit_phone(self) -> None:
        """Plain 10-digit numbers should be replaced with [PHONE]."""
        text = "Call me at 5512345678"
        result = self.anonymizer.anonymize(text)
        assert "[PHONE]" in result

    def test_masks_address(self) -> None:
        """Street addresses should be replaced with [ADDRESS]."""
        text = "I live at 123 Main Street"
        result = self.anonymizer.anonymize(text)
        assert "[ADDRESS]" in result
        assert "123 Main Street" not in result
