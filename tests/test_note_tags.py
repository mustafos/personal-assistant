"""Tests for note tags, filtering, and sorting."""

from uuid import uuid4

import pytest

from assistant.models.note import Note
from assistant.services.note_service import NoteService
from assistant.storage.json_storage import JSONStorage


class InMemoryStorage:
    def __init__(self) -> None:
        self.records: list[dict] = []

    def save(self, records: list[dict]) -> None:
        self.records = [dict(record) for record in records]

    def load(self) -> list[dict]:
        return [dict(record) for record in self.records]


def _note(title: str, tags: list[str] | None = None) -> Note:
    return Note(title=title, content="body", tags=tags or [])


def test_several_tags_can_be_added_and_reloaded(tmp_path) -> None:
    path = tmp_path / "notes.json"
    service = NoteService(JSONStorage(path))
    note = _note("Lecture")
    service.add_note(note)

    service.add_tag(note.id, "School")
    service.add_tag(note.id, "Python")

    reloaded = NoteService(JSONStorage(path)).get_note(note.id)
    assert reloaded is not None
    assert reloaded.tags == ["School", "Python"]


def test_duplicate_tag_is_case_insensitive_noop() -> None:
    service = NoteService(InMemoryStorage())
    note = _note("Lecture")
    service.add_note(note)

    service.add_tag(note.id, "School")
    service.add_tag(note.id, " school ")

    stored = service.get_note(note.id)
    assert stored is not None
    assert stored.tags == ["School"]


def test_find_by_tag_is_case_insensitive() -> None:
    service = NoteService(InMemoryStorage())
    note = _note("Lecture", ["School"])
    service.add_note(note)

    assert [item.id for item in service.find_by_tag("school")] == [note.id]
    assert service.find_by_tag("home") == []


def test_find_by_tag_sorts_by_tags_then_title() -> None:
    service = NoteService(InMemoryStorage())
    zebra = _note("Zebra", ["work", "zoo"])
    alpha = _note("Alpha", ["alpha", "work"])
    service.add_note(zebra)
    service.add_note(alpha)

    assert [note.title for note in service.find_by_tag("work")] == ["Alpha", "Zebra"]


def test_remove_tag_drops_one_tag_and_ignores_a_missing_tag() -> None:
    service = NoteService(InMemoryStorage())
    note = _note("Lecture", ["School", "Python"])
    service.add_note(note)

    service.remove_tag(note.id, "SCHOOL")
    service.remove_tag(note.id, "missing")

    stored = service.get_note(note.id)
    assert stored is not None
    assert stored.tags == ["Python"]


def test_blank_tag_is_rejected() -> None:
    service = NoteService(InMemoryStorage())
    note = _note("Lecture")
    service.add_note(note)

    with pytest.raises(ValueError):
        service.add_tag(note.id, "   ")
    with pytest.raises(ValueError):
        service.remove_tag(note.id, "")
    with pytest.raises(ValueError):
        service.find_by_tag(" ")


def test_unknown_note_raises_lookup_error() -> None:
    service = NoteService(InMemoryStorage())
    missing = uuid4()

    with pytest.raises(LookupError):
        service.add_tag(missing, "school")
    with pytest.raises(LookupError):
        service.remove_tag(missing, "school")
