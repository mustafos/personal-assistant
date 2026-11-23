"""Reusable field values shared by domain models.

These objects store user-entered values. Format rules for phone numbers and
email addresses belong in ``assistant.utils.validators``.
"""

from dataclasses import dataclass


def normalize_label(value: str, *, field_name: str, allow_empty: bool = False) -> str:
    """Collapse whitespace in a short text field.

    Args:
        value: Raw text entered by a caller.
        field_name: Field name used in error messages.
        allow_empty: When True, blank text becomes an empty string.

    Returns:
        Single-spaced text with no leading or trailing whitespace.

    Raises:
        TypeError: If ``value`` is not a string.
        ValueError: If the text is blank and ``allow_empty`` is False.
    """
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string.")
    normalized = " ".join(value.split())
    if not normalized and not allow_empty:
        raise ValueError(f"{field_name} must not be empty.")
    return normalized


@dataclass(frozen=True, slots=True)
class PhoneNumber:
    """A phone number stored as trimmed text.

    This value object does not check the phone format. Call
    ``assistant.utils.validators.is_valid_phone`` before constructing it
    once that rule exists.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("Phone number must be a string.")
        stripped = self.value.strip()
        if not stripped:
            raise ValueError("Phone number must not be empty.")
        # Frozen instances reject normal assignment.
        object.__setattr__(self, "value", stripped)


@dataclass(frozen=True, slots=True)
class EmailAddress:
    """An email address stored as trimmed text.

    Format checking is intentionally left to
    ``assistant.utils.validators.is_valid_email``.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("Email address must be a string.")
        stripped = self.value.strip()
        if not stripped:
            raise ValueError("Email address must not be empty.")
        object.__setattr__(self, "value", stripped)


__all__ = ["EmailAddress", "PhoneNumber", "normalize_label"]
