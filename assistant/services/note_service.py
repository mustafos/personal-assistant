"""Business operations for notes and tags."""

from uuid import UUID

from assistant.models.note import Note
from assistant.storage.storage import Storage


class NoteService:
    """Create, read, search, update, and delete notes.

    Pass a :class:`~assistant.storage.storage.Storage` instance that is
    separate from contact storage. Follow the same load, convert, and save
    pattern as :class:`~assistant.services.contact_service.ContactService`,
    using :meth:`Note.from_dict` and :meth:`Note.to_dict`.

    Tag comparisons are case-insensitive.
    Each method raises ``NotImplementedError`` until it is implemented.
    Other exceptions named on a method describe the contract the
    implementation must follow.
    """

    def __init__(self, storage: Storage) -> None:
        """Store the persistence dependency.

        Args:
            storage: Backend for the note collection.
        """
        self._storage = storage

    def add_note(self, note: Note) -> None:
        """Store a new note.

        Args:
            note: Note to add. Its ``id`` must stay unique.

        Raises:
            NotImplementedError: Saving notes is not implemented yet.
            ValueError: If a note with the same id already exists.
        """
        raise NotImplementedError("NoteService.add_note is not implemented yet.")

    def get_note(self, note_id: UUID) -> Note | None:
        """Return the note with ``note_id``.

        Args:
            note_id: Identifier returned when the note was created.

        Returns:
            The stored note, or None when the id is unknown.

        Raises:
            NotImplementedError: Note lookup is not implemented yet.
        """
        raise NotImplementedError("NoteService.get_note is not implemented yet.")

    def list_notes(self) -> list[Note]:
        """Return every stored note.

        Returns:
            All notes. The order matches the stored collection.

        Raises:
            NotImplementedError: Listing notes is not implemented yet.
        """
        raise NotImplementedError("NoteService.list_notes is not implemented yet.")

    def search_notes(self, query: str) -> list[Note]:
        """Find notes that match ``query``.

        The match is case-insensitive and covers title, content, and tags.

        Args:
            query: Text to look for. Callers should pass a non-empty string.

        Returns:
            Matching notes. An empty list means nothing matched.

        Raises:
            NotImplementedError: Note search is not implemented yet.
        """
        raise NotImplementedError("NoteService.search_notes is not implemented yet.")

    def update_note(self, note: Note) -> None:
        """Replace the stored note that has ``note.id``.

        Args:
            note: New note value, including the id of the note to replace.

        Raises:
            NotImplementedError: Note updates are not implemented yet.
            LookupError: If no stored note uses ``note.id``.
        """
        raise NotImplementedError("NoteService.update_note is not implemented yet.")

    def delete_note(self, note_id: UUID) -> None:
        """Remove the note identified by ``note_id``.

        Args:
            note_id: Identifier of the note to remove.

        Raises:
            NotImplementedError: Note deletion is not implemented yet.
            LookupError: If no stored note uses ``note_id``.
        """
        raise NotImplementedError("NoteService.delete_note is not implemented yet.")

    def add_tag(self, note_id: UUID, tag: str) -> None:
        """Attach ``tag`` to a note.

        Adding a tag that is already present leaves the note unchanged.

        Args:
            note_id: Identifier of the note to change.
            tag: Tag text. Implementations should reject a blank tag.

        Raises:
            NotImplementedError: Tag management is not implemented yet.
            LookupError: If no stored note uses ``note_id``.
            ValueError: If ``tag`` is empty.
        """
        raise NotImplementedError("NoteService.add_tag is not implemented yet.")

    def remove_tag(self, note_id: UUID, tag: str) -> None:
        """Remove ``tag`` from a note.

        Removing a tag that is not present leaves the note unchanged.

        Args:
            note_id: Identifier of the note to change.
            tag: Tag text to remove.

        Raises:
            NotImplementedError: Tag management is not implemented yet.
            LookupError: If no stored note uses ``note_id``.
            ValueError: If ``tag`` is empty.
        """
        raise NotImplementedError("NoteService.remove_tag is not implemented yet.")

    def find_by_tag(self, tag: str) -> list[Note]:
        """Return notes that include ``tag``.

        Args:
            tag: Tag to match, ignoring case.

        Returns:
            Notes that carry the tag. An empty list means nothing matched.

        Raises:
            NotImplementedError: Tag search is not implemented yet.
            ValueError: If ``tag`` is empty.
        """
        raise NotImplementedError("NoteService.find_by_tag is not implemented yet.")


__all__ = ["NoteService"]
