"""CLI command definitions.

Commands are registered here. Handlers check argument shape and stop.
Search, persistence, tag rules, and birthday calculations stay unimplemented
in the service layer.
"""

from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from assistant.services.birthday_service import BirthdayService
from assistant.services.contact_service import ContactService
from assistant.services.note_service import NoteService
from assistant.utils.helpers import normalize_whitespace


@dataclass(frozen=True, slots=True)
class Command:
    """One user-facing command."""

    name: str
    description: str
    usage: str
    handler: Callable[[list[str]], str]


class CommandRegistry:
    """Commands registered when the application starts."""

    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}

    def register(self, command: Command) -> None:
        """Add a command.

        Args:
            command: Command whose name is not already registered.

        Raises:
            ValueError: If ``command.name`` is already registered.
        """
        if command.name in self._commands:
            raise ValueError(f"Command already registered: {command.name}")
        self._commands[command.name] = command

    def get(self, name: str) -> Command | None:
        """Return the command named ``name``, or None when it is absent."""
        return self._commands.get(name)

    def list_commands(self) -> list[Command]:
        """Return commands in registration order."""
        return list(self._commands.values())


class CommandHandler:
    """Scaffold for CLI commands.

    The constructor keeps the services that a future handler will call.
    Methods below only check that the command line has the expected shape.
    """

    def __init__(
        self,
        contacts: ContactService,
        notes: NoteService,
        birthdays: BirthdayService,
    ) -> None:
        """Keep the services reserved for command implementations.

        Args:
            contacts: Contact operations. Use ``Contact.id`` when calling them.
            notes: Note and tag operations. Use ``Note.id`` when calling them.
            birthdays: Upcoming-birthday queries.
        """
        self._contacts = contacts
        self._notes = notes
        self._birthdays = birthdays

    def add_contact(self, args: list[str]) -> str:
        """Scaffold for ``add-contact <name>``."""
        if _require_text(args) is None:
            return "Usage: add-contact <name>"
        raise NotImplementedError

    def list_contacts(self, args: list[str]) -> str:
        """Scaffold for ``list-contacts``."""
        if args:
            return "Usage: list-contacts"
        raise NotImplementedError

    def find_contact(self, args: list[str]) -> str:
        """Scaffold for ``find-contact <id>``."""
        return _unimplemented_id(args, "find-contact <id>")

    def search_contacts(self, args: list[str]) -> str:
        """Scaffold for ``search-contacts <query>``."""
        if _require_text(args) is None:
            return "Usage: search-contacts <query>"
        raise NotImplementedError

    def update_contact(self, args: list[str]) -> str:
        """Scaffold for ``update-contact <id>``."""
        return _unimplemented_id(args, "update-contact <id>")

    def delete_contact(self, args: list[str]) -> str:
        """Scaffold for ``delete-contact <id>``."""
        return _unimplemented_id(args, "delete-contact <id>")

    def add_note(self, args: list[str]) -> str:
        """Scaffold for ``add-note <title>``."""
        if _require_text(args) is None:
            return "Usage: add-note <title>"
        raise NotImplementedError

    def list_notes(self, args: list[str]) -> str:
        """Scaffold for ``list-notes``."""
        if args:
            return "Usage: list-notes"
        raise NotImplementedError

    def find_note(self, args: list[str]) -> str:
        """Scaffold for ``find-note <id>``."""
        return _unimplemented_id(args, "find-note <id>")

    def search_notes(self, args: list[str]) -> str:
        """Scaffold for ``search-notes <query>``."""
        if _require_text(args) is None:
            return "Usage: search-notes <query>"
        raise NotImplementedError

    def update_note(self, args: list[str]) -> str:
        """Scaffold for ``update-note <id>``."""
        return _unimplemented_id(args, "update-note <id>")

    def delete_note(self, args: list[str]) -> str:
        """Scaffold for ``delete-note <id>``."""
        return _unimplemented_id(args, "delete-note <id>")

    def add_tag(self, args: list[str]) -> str:
        """Scaffold for ``add-tag <note-id> <tag>``."""
        parsed = _note_id_and_tag(args, "add-tag <note-id> <tag>")
        if isinstance(parsed, str):
            return parsed
        raise NotImplementedError

    def remove_tag(self, args: list[str]) -> str:
        """Scaffold for ``remove-tag <note-id> <tag>``."""
        parsed = _note_id_and_tag(args, "remove-tag <note-id> <tag>")
        if isinstance(parsed, str):
            return parsed
        raise NotImplementedError

    def notes_by_tag(self, args: list[str]) -> str:
        """Scaffold for ``notes-by-tag <tag>``."""
        if _require_text(args) is None:
            return "Usage: notes-by-tag <tag>"
        raise NotImplementedError

    def birthdays(self, args: list[str]) -> str:
        """Scaffold for ``birthdays [days]``.

        When ``days`` is omitted, the intended window is 7 days.
        """
        if len(args) > 1:
            return "Usage: birthdays [days]"
        if args:
            try:
                days = int(args[0])
            except ValueError:
                return "Usage: birthdays [days]"
            if days < 0:
                return "Days must be zero or greater."
        raise NotImplementedError


def build_registry(handler: CommandHandler) -> CommandRegistry:
    """Register the contact, note, and birthday commands.

    Args:
        handler: Object that implements the command methods.

    Returns:
        A registry in display order.
    """
    specs: tuple[tuple[str, str, str, Callable[[list[str]], str]], ...] = (
        ("add-contact", "Add a contact", "add-contact <name>", handler.add_contact),
        ("list-contacts", "List all contacts", "list-contacts", handler.list_contacts),
        (
            "find-contact",
            "Show a contact by id",
            "find-contact <id>",
            handler.find_contact,
        ),
        (
            "search-contacts",
            "Search contacts",
            "search-contacts <query>",
            handler.search_contacts,
        ),
        (
            "update-contact",
            "Update a contact",
            "update-contact <id>",
            handler.update_contact,
        ),
        (
            "delete-contact",
            "Delete a contact",
            "delete-contact <id>",
            handler.delete_contact,
        ),
        ("add-note", "Add a note", "add-note <title>", handler.add_note),
        ("list-notes", "List all notes", "list-notes", handler.list_notes),
        ("find-note", "Show a note by id", "find-note <id>", handler.find_note),
        ("search-notes", "Search notes", "search-notes <query>", handler.search_notes),
        ("update-note", "Update a note", "update-note <id>", handler.update_note),
        ("delete-note", "Delete a note", "delete-note <id>", handler.delete_note),
        (
            "add-tag",
            "Add a tag to a note",
            "add-tag <note-id> <tag>",
            handler.add_tag,
        ),
        (
            "remove-tag",
            "Remove a tag from a note",
            "remove-tag <note-id> <tag>",
            handler.remove_tag,
        ),
        (
            "notes-by-tag",
            "List notes with a tag",
            "notes-by-tag <tag>",
            handler.notes_by_tag,
        ),
        (
            "birthdays",
            "Show upcoming birthdays (default: 7 days)",
            "birthdays [days]",
            handler.birthdays,
        ),
    )
    registry = CommandRegistry()
    for name, description, usage, command_handler in specs:
        registry.register(
            Command(
                name=name,
                description=description,
                usage=usage,
                handler=command_handler,
            )
        )
    return registry


def _require_text(args: list[str]) -> str | None:
    """Join arguments into cleaned text, or None when the line has no text."""
    if not args:
        return None
    text = normalize_whitespace(" ".join(args))
    if not text:
        return None
    return text


def _require_id(args: list[str], usage: str) -> UUID | str:
    """Parse a single UUID argument, or return a usage message."""
    if len(args) != 1:
        return f"Usage: {usage}"
    try:
        return UUID(args[0])
    except ValueError:
        return "Id must be a valid UUID."


def _unimplemented_id(args: list[str], usage: str) -> str:
    """Accept one UUID, then leave the command unimplemented."""
    parsed = _require_id(args, usage)
    if isinstance(parsed, str):
        return parsed
    raise NotImplementedError


def _note_id_and_tag(args: list[str], usage: str) -> tuple[UUID, str] | str:
    """Parse a note id and the remaining text as a tag."""
    if len(args) < 2:
        return f"Usage: {usage}"
    try:
        note_id = UUID(args[0])
    except ValueError:
        return "Note id must be a valid UUID."
    tag = normalize_whitespace(" ".join(args[1:]))
    if not tag:
        return f"Usage: {usage}"
    return note_id, tag


__all__ = ["Command", "CommandHandler", "CommandRegistry", "build_registry"]
