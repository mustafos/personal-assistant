"""Reusable validation functions.

The phone and email rules are not defined yet. Keep those rules here so the
CLI and the services can share them later.
"""


def is_valid_phone(value: str) -> bool:
    """Return whether ``value`` is an acceptable phone number.

    Args:
        value: Candidate phone number.

    Returns:
        This function does not return until the rule is implemented.

    Raises:
        TypeError: If ``value`` is not a string.
        NotImplementedError: Phone rules are not defined yet.
    """
    if not isinstance(value, str):
        raise TypeError("Phone number must be a string.")
    raise NotImplementedError("Phone validation is not implemented yet.")


def is_valid_email(value: str) -> bool:
    """Return whether ``value`` is an acceptable email address.

    Args:
        value: Candidate email address.

    Returns:
        This function does not return until the rule is implemented.

    Raises:
        TypeError: If ``value`` is not a string.
        NotImplementedError: Email rules are not defined yet.
    """
    if not isinstance(value, str):
        raise TypeError("Email address must be a string.")
    raise NotImplementedError("Email validation is not implemented yet.")


__all__ = ["is_valid_email", "is_valid_phone"]
