from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


def _normalize_tags(tags: list[str]) -> list[str]:
  if not isinstance(tags, list):
    raise TypeError("Невірний формат тегів. Очікується список.")

  result: list[str] = []
  seen: set[str] = set()

  for tag in tags:
    if isinstance(tag, str):
      cleaned = tag.strip().lower()
      if cleaned and cleaned not in seen:
        seen.add(cleaned)
        result.append(cleaned)

  return result


@dataclass(slots=True)
class Note:
    title: str
    content: str = ""
    tags: list[str] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if isinstance(self.id, str):
            self.id = UUID(self.id)
        self.title = str(self.title).strip()
        self.content = str(self.content)
        self.tags = _normalize_tags(self.tags)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Note:
        raw_id = data.get("id")
        note_id = UUID(str(raw_id)) if raw_id is not None else uuid4()
        return cls(
            id=note_id,
            title=str(data.get("title", "")),
            content=str(data.get("content", "")),
            tags=_normalize_tags(data.get("tags")),
        )
