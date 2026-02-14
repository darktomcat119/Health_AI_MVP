"""PII anonymization service.

Strips personally identifiable information from user messages
before they are processed by the LLM or stored in logs.
Uses compiled regex patterns for performance.

Supported PII types:
- Email addresses
- Mexican phone numbers (+52, 55-XXXX-XXXX, 10-digit)
- Names (after "my name is", "I'm", "me llamo", "soy")
- Street addresses (number + street patterns)
"""

import logging
import re

logger = logging.getLogger(__name__)

# Compiled patterns for each PII type
_EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
)

_PHONE_PATTERN = re.compile(
    r"(?:\+52\s?)?"            # optional country code
    r"(?:\(?\d{2,3}\)?[-\s]?)" # area code with optional dash/space
    r"(?:\d{4}[-\s]?\d{4})"   # subscriber number
    r"|\b\d{10}\b"            # plain 10-digit number
)

_NAME_PATTERN = re.compile(
    r"(?:my name is|i'?m|me llamo|soy)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    re.IGNORECASE,
)

_ADDRESS_PATTERN = re.compile(
    r"\b\d{1,5}\s+(?:[A-Z][a-z]+\s?){1,4}"
    r"(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr"
    r"|Lane|Ln|Court|Ct|Calle|Avenida|Av)\b",
    re.IGNORECASE,
)


class Anonymizer:
    """Strips PII from text using compiled regex patterns.

    Replaces detected PII with bracketed placeholders:
    [EMAIL], [PHONE], [NAME], [ADDRESS].
    Logs that PII was detected but never logs the actual content.
    """

    def anonymize(self, text: str) -> str:
        """Remove all detected PII from the given text.

        Args:
            text: Raw user message that may contain PII.

        Returns:
            Anonymized text with PII replaced by placeholders.
        """
        result = text
        pii_found = False

        result, email_found = self._replace_emails(result)
        pii_found = pii_found or email_found

        result, phone_found = self._replace_phones(result)
        pii_found = pii_found or phone_found

        result, name_found = self._replace_names(result)
        pii_found = pii_found or name_found

        result, address_found = self._replace_addresses(result)
        pii_found = pii_found or address_found

        if pii_found:
            logger.info("PII detected and anonymized in user message")

        return result

    def _replace_emails(self, text: str) -> tuple[str, bool]:
        """Replace email addresses with [EMAIL].

        Args:
            text: Input text.

        Returns:
            Tuple of (modified text, whether any emails were found).
        """
        new_text = _EMAIL_PATTERN.sub("[EMAIL]", text)
        return new_text, new_text != text

    def _replace_phones(self, text: str) -> tuple[str, bool]:
        """Replace phone numbers with [PHONE].

        Args:
            text: Input text.

        Returns:
            Tuple of (modified text, whether any phones were found).
        """
        new_text = _PHONE_PATTERN.sub("[PHONE]", text)
        return new_text, new_text != text

    def _replace_names(self, text: str) -> tuple[str, bool]:
        """Replace names following identity phrases with [NAME].

        Args:
            text: Input text.

        Returns:
            Tuple of (modified text, whether any names were found).
        """
        found = False

        def _replace_match(match: re.Match) -> str:
            nonlocal found
            found = True
            prefix = match.group(0)[: match.start(1) - match.start(0)]
            return f"{prefix}[NAME]"

        new_text = _NAME_PATTERN.sub(_replace_match, text)
        return new_text, found

    def _replace_addresses(self, text: str) -> tuple[str, bool]:
        """Replace street addresses with [ADDRESS].

        Args:
            text: Input text.

        Returns:
            Tuple of (modified text, whether any addresses were found).
        """
        new_text = _ADDRESS_PATTERN.sub("[ADDRESS]", text)
        return new_text, new_text != text
