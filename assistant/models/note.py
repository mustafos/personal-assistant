"""Note entity."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from assistant.models.fields import normalize_label


@dataclass(slots=True)
class Note:
    """A note with a stable identifier, text, and tags.

    ``id`` is generated with ``uuid4`` when the caller does not supply one.
    Persistence code should convert instances with :meth:`to_dict` and
    restore them with :meth:`from_dict`.
    """

    title: str
    content: str = ""
    tags: list[str] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.title = normalize_label(self.title, field_name="Note title")
        if not isinstance(self.content, str):
            raise TypeError("Note content must be a string.")
        self.content = self.content.strip()
        if not isinstance(self.id, UUID):
            raise TypeError("Note id must be a UUID.")
        self.tags = [normalize_label(tag, field_name="Tag") for tag in self.tags]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready mapping.

        ``id`` is stored as a canonical UUID string.
        """
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Note":
        """Rebuild a note from :meth:`to_dict` output.

        Args:
            data: Mapping with ``id``, ``title``, and optional note fields.

        Returns:
            A new note that keeps the stored id.

        Raises:
            TypeError: If ``data`` or a field has an unexpected type.
            KeyError: If ``title`` is missing.
            ValueError: If ``id`` is not a UUID or a field value is unusable.
        """
        if not isinstance(data, dict):
            raise TypeError("Note data must be a mapping.")

        note_id = data.get("id")
        if not isinstance(note_id, str):
            raise TypeError("Note field 'id' must be a string.")

        tags_raw = data.get("tags", [])
        if not isinstance(tags_raw, list):
            raise TypeError("Note field 'tags' must be a list.")

        content = data.get("content", "")
        if not isinstance(content, str):
            raise TypeError("Note field 'content' must be a string.")

        title = data["title"]
        if not isinstance(title, str):
            raise TypeError("Note field 'title' must be a string.")

        return cls(title=title, content=content, tags=tags_raw, id=UUID(note_id))


__all__ = ["Note"]
