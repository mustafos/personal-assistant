from uuid import UUID

from assistant.models.note import Note
from assistant.storage.storage import Storage

__all__ = ["NoteService"]


class NoteService:
    """Create, read, search, update, and delete notes."""

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    def _load_notes(self) -> list[Note]:
        return [Note.from_dict(item) for item in self._storage.load()]

    def _save_notes(self, notes: list[Note]) -> None:
        self._storage.save([note.to_dict() for note in notes])

    def add_note(self, note: Note) -> None:
        notes = self._load_notes()
        if any(existing.id == note.id for existing in notes):
            raise ValueError(f"Note with id {note.id} already exists.")
        notes.append(note)
        self._save_notes(notes)

    def get_note(self, note_id: UUID) -> Note | None:
        for note in self._load_notes():
            if note.id == note_id:
                return note
        return None

    def list_notes(self) -> list[Note]:
        return self._load_notes()

    def search_notes(self, query: str) -> list[Note]:
        normalized = query.lower()
        return [
            note
            for note in self._load_notes()
            if normalized in note.title.lower()
            or normalized in note.content.lower()
            or any(normalized in tag.lower() for tag in note.tags)
        ]

    def update_note(self, note: Note) -> None:
        notes = self._load_notes()
        for index, existing in enumerate(notes):
            if existing.id == note.id:
                notes[index] = note
                self._save_notes(notes)
                return
        raise LookupError(f"Note with id {note.id} not found.")

    def delete_note(self, note_id: UUID) -> None:
        notes = self._load_notes()
        filtered = [note for note in notes if note.id != note_id]
        if len(filtered) == len(notes):
            raise LookupError(f"Note with id {note_id} not found.")
        self._save_notes(filtered)

    def add_tag(self, note_id: UUID, tag: str) -> None:
        raise NotImplementedError("NoteService.add_tag is not implemented yet.")

    def remove_tag(self, note_id: UUID, tag: str) -> None:
        raise NotImplementedError(
            "NoteService.remove_tag is not implemented yet."
        )

    def find_by_tag(self, tag: str) -> list[Note]:
        raise NotImplementedError(
            "NoteService.find_by_tag is not implemented yet."
        )