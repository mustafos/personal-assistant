"""Small helpers with no application rules.

Phone and email checks live in ``assistant.utils.validators``.
"""

from datetime import date


def normalize_whitespace(value: str) -> str:
    """Collapse internal whitespace and strip the ends.

    Args:
        value: Text to clean.

    Returns:
        A single-spaced string. Blank input becomes an empty string.

    Raises:
        TypeError: If ``value`` is not a string.
    """
    if not isinstance(value, str):
        raise TypeError("value must be a string.")
    return " ".join(value.split())


def parse_iso_date(value: str) -> date:
    """Parse a calendar date written as ``YYYY-MM-DD``.

    Args:
        value: ISO date string.

    Returns:
        The corresponding date.

    Raises:
        ValueError: If ``value`` is not a valid ISO date.
    """
    if not isinstance(value, str):
        raise TypeError("value must be a string.")
    return date.fromisoformat(value)


__all__ = ["normalize_whitespace", "parse_iso_date"]
