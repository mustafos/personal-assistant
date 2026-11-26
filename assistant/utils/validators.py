"""Phone and email checks shared by the CLI and the services."""

import re

PHONE_PATTERN = re.compile(r"\+\d{8,15}")
EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"
)


def is_valid_phone(value: str) -> bool:
    """Return whether ``value`` is an acceptable phone number.

    Args:
        value: Candidate phone number.

    Returns:
        True when ``value`` is a leading ``+`` followed by 8 to 15 digits.
        Spaces and hyphens are ignored. Parentheses are rejected.

    Raises:
        TypeError: If ``value`` is not a string.
    """
    if not isinstance(value, str):
        raise TypeError("Phone number must be a string.")
    cleaned = re.sub(r"[\s-]", "", value)
    return PHONE_PATTERN.fullmatch(cleaned) is not None


def is_valid_email(value: str) -> bool:
    """Return whether ``value`` is an acceptable email address.

    Args:
        value: Candidate email address.

    Returns:
        True when ``value`` has a local part, ``@``, a domain, and a
        top-level label of at least two letters.

    Raises:
        TypeError: If ``value`` is not a string.
    """
    if not isinstance(value, str):
        raise TypeError("Email address must be a string.")
    cleaned = value.strip()
    return EMAIL_PATTERN.fullmatch(cleaned) is not None


__all__ = ["is_valid_email", "is_valid_phone"]
