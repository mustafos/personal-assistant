"""Business operations for notes and tags."""

from uuid import UUID

from assistant.models.note import Note
from assistant.storage.storage import Storage


class NoteService:
    """Create, read, search, update, and delete notes.

    Pass a :class:`~assistant.storage.storage.Storage` instance that is
    separate from contact storage. Load records with ``storage.load()``,
    rebuild them with :meth:`Note.from_dict`, and save ``note.to_dict()``
    mappings with ``storage.save``. Match a stored record by ``Note.id``.

    Tag comparisons are case-insensitive.
    """

    def __init__(self, storage: Storage) -> None:
        """Store the persistence dependency.

        Args:
            storage: Backend for the note collection.
        """
        self._storage = storage

    def _load_notes(self) -> list[Note]:
        """Load stored note records and rebuild Note instances."""
        raw_records = self._storage.load()
        return [Note.from_dict(record) for record in raw_records]

    def _save_notes(self, notes: list[Note]) -> None:
        """Serialize Note instances and persist them via storage."""
        self._storage.save([note.to_dict() for note in notes])

    @staticmethod
    def _normalize_tag(tag: str) -> str:
        """Validate and trim a tag string, raising ValueError if blank."""
        cleaned = " ".join(tag.strip().split())
        if not cleaned:
            raise ValueError("Tag must not be empty.")
        return cleaned

    @staticmethod
    def _matches_query(note: Note, needle: str) -> bool:
        """Check whether title, content, or any tag contains the lowercased needle."""
        parts: list[str] = [note.title, note.content]
        parts.extend(note.tags)
        return any(needle in part.casefold() for part in parts)

    def add_note(self, note: Note) -> None:
        """Store a new note.

        Args:
            note: Note to add. Its ``id`` must stay unique.

        Raises:
            ValueError: If a note with the same id already exists.
        """
        notes = self._load_notes()
        if any(existing.id == note.id for existing in notes):
            raise ValueError(f"Note with id {note.id} already exists.")

        notes.append(note)
        self._save_notes(notes)

    def get_note(self, note_id: UUID) -> Note | None:
        """Return the note with ``note_id``.

        Args:
            note_id: Identifier returned when the note was created.

        Returns:
            The stored note, or None when the id is unknown.
        """
        for note in self._load_notes():
            if note.id == note_id:
                return note
        return None

    def list_notes(self) -> list[Note]:
        """Return every stored note.

        Returns:
            All notes. The order matches the stored collection.
        """
        return self._load_notes()

    def search_notes(self, query: str) -> list[Note]:
        """Find notes that match ``query``.

        The match is case-insensitive and covers title, content, and tags.

        Args:
            query: Text to look for. Callers should pass a non-empty string.

        Returns:
            Matching notes. An empty list means nothing matched.
        """
        needle = " ".join(query.strip().split()).casefold()
        if not needle:
            return []

        return [
            note
            for note in self._load_notes()
            if self._matches_query(note, needle)
        ]

    def update_note(self, note: Note) -> None:
        """Replace the stored note that has ``note.id``.

        Args:
            note: New note value, including the id of the note to replace.

        Raises:
            LookupError: If no stored note uses ``note.id``.
        """
        notes = self._load_notes()
        for index, existing in enumerate(notes):
            if existing.id == note.id:
                notes[index] = note
                self._save_notes(notes)
                return

        raise LookupError(f"Note not found: {note.id}")

    def delete_note(self, note_id: UUID) -> None:
        """Remove the note identified by ``note_id``.

        Args:
            note_id: Identifier of the note to remove.

        Raises:
            LookupError: If no stored note uses ``note_id``.
        """
        notes = self._load_notes()
        remaining = [existing for existing in notes if existing.id != note_id]
        if len(remaining) == len(notes):
            raise LookupError(f"Note not found: {note_id}")

        self._save_notes(remaining)

    def add_tag(self, note_id: UUID, tag: str) -> None:
        """Attach ``tag`` to a note.

        Adding a tag that is already present leaves the note unchanged.

        Args:
            note_id: Identifier of the note to change.
            tag: Tag text. Implementations should reject a blank tag.

        Raises:
            LookupError: If no stored note uses ``note_id``.
            ValueError: If ``tag`` is empty.
        """
        cleaned_tag = self._normalize_tag(tag)
        notes = self._load_notes()

        for index, existing in enumerate(notes):
            if existing.id == note_id:
                if any(t.casefold() == cleaned_tag.casefold() for t in existing.tags):
                    return

                updated_tags = [*existing.tags, cleaned_tag]
                notes[index] = Note(
                    title=existing.title,
                    content=existing.content,
                    tags=updated_tags,
                    id=existing.id,
                )
                self._save_notes(notes)
                return

        raise LookupError(f"Note not found: {note_id}")

    def remove_tag(self, note_id: UUID, tag: str) -> None:
        """Remove ``tag`` from a note.

        Removing a tag that is not present leaves the note unchanged.

        Args:
            note_id: Identifier of the note to change.
            tag: Tag text to remove.

        Raises:
            LookupError: If no stored note uses ``note_id``.
            ValueError: If ``tag`` is empty.
        """
        cleaned_tag = self._normalize_tag(tag)
        notes = self._load_notes()

        for index, existing in enumerate(notes):
            if existing.id == note_id:
                remaining_tags = [
                    t for t in existing.tags if t.casefold() != cleaned_tag.casefold()
                ]
                if len(remaining_tags) == len(existing.tags):
                    return

                notes[index] = Note(
                    title=existing.title,
                    content=existing.content,
                    tags=remaining_tags,
                    id=existing.id,
                )
                self._save_notes(notes)
                return

        raise LookupError(f"Note not found: {note_id}")

    def find_by_tag(self, tag: str) -> list[Note]:
        """Return notes that include ``tag``.

        Args:
            tag: Tag to match, ignoring case.

        Returns:
            Notes that carry the tag. An empty list means nothing matched.

        Raises:
            ValueError: If ``tag`` is empty.
        """
        cleaned_tag = self._normalize_tag(tag).casefold()
        return [
            note
            for note in self._load_notes()
            if any(t.casefold() == cleaned_tag for t in note.tags)
        ]


__all__ = ["NoteService"]
