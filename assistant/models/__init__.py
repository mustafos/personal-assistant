"""Domain models for contacts and notes."""

from assistant.models.contact import Contact
from assistant.models.fields import EmailAddress, PhoneNumber, normalize_label
from assistant.models.note import Note

__all__ = [
    "Contact",
    "EmailAddress",
    "Note",
    "PhoneNumber",
    "normalize_label",
]
