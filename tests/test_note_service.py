from uuid import UUID, uuid4

import pytest

from assistant.models.note import Note
from assistant.services.note_service import NoteService


class InMemoryStorage:
    def __init__(self, initial: list[dict] | None = None) -> None:
        self._items: list[dict] = [dict(item) for item in (initial or [])]

    def load(self) -> list[dict]:
        return [dict(item) for item in self._items]

    def save(self, data: list[dict]) -> None:
        self._items = [dict(item) for item in data]


def _make_note(
    title: str = "Title",
    content: str = "Content",
    tags: list[str] | None = None,
    note_id: UUID | None = None,
) -> Note:
    return Note(
        id=note_id or uuid4(),
        title=title,
        content=content,
        tags=tags if tags is not None else [],
    )


def test_add_and_get_note() -> None:
    storage = InMemoryStorage()
    service = NoteService(storage)
    note = _make_note(title="Shopping", content="Buy milk", tags=["home"])

    service.add_note(note)
    loaded = service.get_note(note.id)

    assert loaded is not None
    assert loaded.id == note.id
    assert loaded.title == "Shopping"
    assert loaded.content == "Buy milk"
    assert loaded.tags == ["home"]


def test_add_duplicate_note_raises() -> None:
    note_id = uuid4()
    storage = InMemoryStorage()
    service = NoteService(storage)
    service.add_note(_make_note(title="First", note_id=note_id))

    with pytest.raises(ValueError):
        service.add_note(_make_note(title="Second", note_id=note_id))


def test_get_unknown_note_returns_none() -> None:
    service = NoteService(InMemoryStorage())
    assert service.get_note(uuid4()) is None


def test_list_notes_preserves_order() -> None:
    service = NoteService(InMemoryStorage())
    n1 = _make_note(title="One")
    n2 = _make_note(title="Two")
    service.add_note(n1)
    service.add_note(n2)

    notes = service.list_notes()
    assert [n.id for n in notes] == [n1.id, n2.id]


def test_search_notes_case_insensitive_partial() -> None:
    service = NoteService(InMemoryStorage())
    n1 = _make_note(title="Python Tips", content="Use pytest", tags=["dev"])
    n2 = _make_note(title="Grocery", content="Apples and bananas", tags=["food"])
    service.add_note(n1)
    service.add_note(n2)

    assert [n.id for n in service.search_notes("python")] == [n1.id]
    assert [n.id for n in service.search_notes("PYTEST")] == [n1.id]
    assert [n.id for n in service.search_notes("anan")] == [n2.id]
    assert service.search_notes("nonexistent") == []


def test_update_note() -> None:
    service = NoteService(InMemoryStorage())
    note = _make_note(title="Draft", content="Old text")
    service.add_note(note)

    updated = _make_note(title="Final", content="New text", note_id=note.id)
    service.update_note(updated)

    loaded = service.get_note(note.id)
    assert loaded is not None
    assert loaded.title == "Final"
    assert loaded.content == "New text"


def test_update_missing_note_raises() -> None:
    service = NoteService(InMemoryStorage())
    with pytest.raises(LookupError):
        service.update_note(_make_note(title="Missing"))


def test_delete_note() -> None:
    service = NoteService(InMemoryStorage())
    note = _make_note(title="Temp")
    service.add_note(note)

    service.delete_note(note.id)
    assert service.get_note(note.id) is None
    assert service.list_notes() == []


def test_delete_missing_note_raises() -> None:
    service = NoteService(InMemoryStorage())
    with pytest.raises(LookupError):
        service.delete_note(uuid4())
