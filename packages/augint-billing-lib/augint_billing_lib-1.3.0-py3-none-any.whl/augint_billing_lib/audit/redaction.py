"""Sensitive data redaction for audit logs.

This module provides production-grade PII and sensitive data redaction
with pre-compiled patterns for performance.
"""

import re
from dataclasses import dataclass
from re import Pattern
from typing import Any, ClassVar, Union


@dataclass
class RedactionPattern:
    """Pattern for identifying and redacting sensitive data."""

    name: str
    pattern: Pattern[str]
    replacement: str = "***REDACTED***"


class SensitiveDataRedactor:
    """Production-grade sensitive data redaction.

    Features:
    - Pre-compiled regex patterns for performance
    - Depth limits to prevent infinite recursion
    - Key-based detection for sensitive fields
    - Pattern-based detection in strings
    """

    # Pre-compiled patterns for performance
    PATTERNS: ClassVar[list[RedactionPattern]] = [
        RedactionPattern(
            "email",
            re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        ),
        RedactionPattern(
            "phone",
            re.compile(r"(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}"),
        ),
        RedactionPattern(
            "ssn",
            re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b"),
        ),
        RedactionPattern(
            "credit_card",
            re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
        ),
        RedactionPattern(
            "stripe_key",
            re.compile(r"\b(sk|pk|rk)_(test|live)_[A-Za-z0-9]{24,}\b"),
        ),
        RedactionPattern(
            "api_key",
            re.compile(r"\b[A-Za-z0-9]{32,64}\b"),
        ),
        RedactionPattern(
            "jwt_token",
            re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
        ),
        RedactionPattern(
            "uuid",
            re.compile(
                r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
                re.IGNORECASE,
            ),
        ),
        RedactionPattern(
            "password_pattern",
            re.compile(r"(password|secret|pass)\s*[:=]\s*\S+", re.IGNORECASE),
            "***REDACTED***",
        ),
    ]

    # Sensitive keys that should always be redacted
    SENSITIVE_KEYS: ClassVar[set[str]] = {
        "password",
        "secret",
        "token",
        "api_key",
        "private_key",
        "ssn",
        "social_security_number",
        "credit_card",
        "card_number",
        "cvv",
        "pin",
        "bank_account",
        "routing_number",
        "stripe_key",
        "client_secret",
        "webhook_secret",
        "access_token",
        "refresh_token",
        "auth_token",
        "bearer_token",
        "session_id",
        "csrf_token",
    }

    @classmethod
    def redact(cls, data: Any, max_depth: int = 10) -> Any:
        """Recursively redact sensitive data with depth limit.

        Args:
            data: Data to redact (any type)
            max_depth: Maximum recursion depth

        Returns:
            Redacted copy of the data
        """
        if max_depth <= 0:
            return "***DEPTH_LIMIT_EXCEEDED***"

        if isinstance(data, dict):
            return cls._redact_dict(data, max_depth - 1)
        if isinstance(data, (list, tuple)):
            return cls._redact_sequence(data, max_depth - 1)
        if isinstance(data, str):
            return cls._redact_string(data)
        # Numbers, booleans, None, etc. - return as-is
        return data

    @classmethod
    def _redact_dict(cls, data: dict[str, Any], depth: int) -> dict[str, Any]:
        """Redact dictionary with key-based and pattern-based detection."""
        result: dict[str, Any] = {}

        for key, value in data.items():
            # Check if key indicates sensitive data
            key_lower = key.lower()
            if any(sensitive_key in key_lower for sensitive_key in cls.SENSITIVE_KEYS):
                result[key] = "***REDACTED***"
            else:
                # Recursively redact the value
                result[key] = cls.redact(value, depth)

        return result

    @classmethod
    def _redact_sequence(
        cls, data: Union[list[Any], tuple[Any, ...]], depth: int
    ) -> Union[list[Any], tuple[Any, ...]]:
        """Redact list or tuple elements."""
        redacted_items = [cls.redact(item, depth) for item in data]

        # Return the same type as input
        if isinstance(data, tuple):
            return tuple(redacted_items)
        return redacted_items

    @classmethod
    def _redact_string(cls, data: str) -> str:
        """Apply pattern-based redaction to strings."""
        result = data

        for pattern_info in cls.PATTERNS:
            result = pattern_info.pattern.sub(pattern_info.replacement, result)

        return result

    @classmethod
    def is_sensitive_key(cls, key: str) -> bool:
        """Check if a key name indicates sensitive data.

        Args:
            key: Dictionary key to check

        Returns:
            True if key is considered sensitive
        """
        key_lower = key.lower()
        return any(sensitive_key in key_lower for sensitive_key in cls.SENSITIVE_KEYS)

    @classmethod
    def add_pattern(cls, name: str, pattern: str, replacement: str = "***REDACTED***") -> None:
        """Add a custom redaction pattern.

        Args:
            name: Pattern name for identification
            pattern: Regular expression pattern
            replacement: Replacement string
        """
        compiled_pattern = re.compile(pattern)
        cls.PATTERNS.append(RedactionPattern(name, compiled_pattern, replacement))

    @classmethod
    def remove_pattern(cls, name: str) -> bool:
        """Remove a redaction pattern by name.

        Args:
            name: Pattern name to remove

        Returns:
            True if pattern was found and removed
        """
        original_length = len(cls.PATTERNS)
        cls.PATTERNS[:] = [p for p in cls.PATTERNS if p.name != name]
        return len(cls.PATTERNS) < original_length
