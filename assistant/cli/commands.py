"""CLI command definitions.

Handlers parse arguments and call services. Duplicate checks, search matching,
tag rules, and birthday calculations stay in the service layer.
"""

from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from assistant.models.contact import Contact
from assistant.models.note import Note
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
    """Parse CLI arguments and delegate to services."""

    def __init__(
        self,
        contacts: ContactService,
        notes: NoteService,
        birthdays: BirthdayService,
    ) -> None:
        """Keep the services used by command handlers.

        Args:
            contacts: Contact operations.
            notes: Note and tag operations.
            birthdays: Upcoming-birthday queries.
        """
        self._contacts = contacts
        self._notes = notes
        self._birthdays = birthdays

    def add_contact(self, args: list[str]) -> str:
        """Handle ``add-contact <name>``."""
        name = _require_text(args)
        if name is None:
            return "Usage: add-contact <name>"
        contact = Contact(name=name)
        self._contacts.add_contact(contact)
        return f"Added contact '{contact.name}'."

    def list_contacts(self, args: list[str]) -> str:
        """Handle ``list-contacts``."""
        if args:
            return "Usage: list-contacts"
        contacts = self._contacts.list_contacts()
        if not contacts:
            return "No contacts saved."
        return "\n".join(contact.name for contact in contacts)

    def find_contact(self, args: list[str]) -> str:
        """Handle ``find-contact <name>``."""
        name = _require_text(args)
        if name is None:
            return "Usage: find-contact <name>"
        contact = self._contacts.get_contact(name)
        if contact is None:
            return f"No contact named '{name}'."
        return _format_contact(contact)

    def search_contacts(self, args: list[str]) -> str:
        """Handle ``search-contacts <query>``."""
        query = _require_text(args)
        if query is None:
            return "Usage: search-contacts <query>"
        matches = self._contacts.search_contacts(query)
        if not matches:
            return "No contacts found."
        return "\n".join(contact.name for contact in matches)

    def update_contact(self, args: list[str]) -> str:
        """Handle ``update-contact <name>``.

        Editing individual fields from the command line is not available yet.
        """
        if _require_text(args) is None:
            return "Usage: update-contact <name>"
        raise NotImplementedError

    def delete_contact(self, args: list[str]) -> str:
        """Handle ``delete-contact <name>``."""
        name = _require_text(args)
        if name is None:
            return "Usage: delete-contact <name>"
        self._contacts.delete_contact(name)
        return f"Deleted contact '{name}'."

    def add_note(self, args: list[str]) -> str:
        """Handle ``add-note <title>``.

        The note content is empty until note editing is implemented.
        """
        title = _require_text(args)
        if title is None:
            return "Usage: add-note <title>"
        note = Note(title=title, content="")
        self._notes.add_note(note)
        return f"Added note '{note.title}' ({note.id})."

    def list_notes(self, args: list[str]) -> str:
        """Handle ``list-notes``."""
        if args:
            return "Usage: list-notes"
        notes = self._notes.list_notes()
        if not notes:
            return "No notes saved."
        return "\n".join(f"{note.id}  {note.title}" for note in notes)

    def find_note(self, args: list[str]) -> str:
        """Handle ``find-note <id>``."""
        note_id = _require_note_id(args, "find-note <id>")
        if isinstance(note_id, str):
            return note_id
        note = self._notes.get_note(note_id)
        if note is None:
            return f"No note with id '{note_id}'."
        return _format_note(note)

    def search_notes(self, args: list[str]) -> str:
        """Handle ``search-notes <query>``."""
        query = _require_text(args)
        if query is None:
            return "Usage: search-notes <query>"
        matches = self._notes.search_notes(query)
        if not matches:
            return "No notes found."
        return "\n".join(f"{note.id}  {note.title}" for note in matches)

    def update_note(self, args: list[str]) -> str:
        """Handle ``update-note <id>``.

        Editing note fields from the command line is not available yet.
        """
        note_id = _require_note_id(args, "update-note <id>")
        if isinstance(note_id, str):
            return note_id
        raise NotImplementedError

    def delete_note(self, args: list[str]) -> str:
        """Handle ``delete-note <id>``."""
        note_id = _require_note_id(args, "delete-note <id>")
        if isinstance(note_id, str):
            return note_id
        self._notes.delete_note(note_id)
        return f"Deleted note '{note_id}'."

    def add_tag(self, args: list[str]) -> str:
        """Handle ``add-tag <note-id> <tag>``."""
        parsed = _note_id_and_tag(args, "add-tag <note-id> <tag>")
        if isinstance(parsed, str):
            return parsed
        note_id, tag = parsed
        self._notes.add_tag(note_id, tag)
        return f"Added tag '{tag}' to note '{note_id}'."

    def remove_tag(self, args: list[str]) -> str:
        """Handle ``remove-tag <note-id> <tag>``."""
        parsed = _note_id_and_tag(args, "remove-tag <note-id> <tag>")
        if isinstance(parsed, str):
            return parsed
        note_id, tag = parsed
        self._notes.remove_tag(note_id, tag)
        return f"Removed tag '{tag}' from note '{note_id}'."

    def notes_by_tag(self, args: list[str]) -> str:
        """Handle ``notes-by-tag <tag>``."""
        tag = _require_text(args)
        if tag is None:
            return "Usage: notes-by-tag <tag>"
        matches = self._notes.find_by_tag(tag)
        if not matches:
            return f"No notes tagged '{tag}'."
        return "\n".join(f"{note.id}  {note.title}" for note in matches)

    def birthdays(self, args: list[str]) -> str:
        """Handle ``birthdays [days]``.

        When ``days`` is omitted, the window is 7 days.
        """
        if len(args) > 1:
            return "Usage: birthdays [days]"
        days = 7
        if args:
            try:
                days = int(args[0])
            except ValueError:
                return "Usage: birthdays [days]"
        if days < 0:
            return "Days must be zero or greater."
        matches = self._birthdays.upcoming_birthdays(days)
        unit = "day" if days == 1 else "days"
        if not matches:
            return f"No birthdays in the next {days} {unit}."
        lines = [f"Birthdays in the next {days} {unit}:"]
        for contact in matches:
            shown = contact.birthday.isoformat() if contact.birthday else "unknown"
            lines.append(f"{contact.name} ({shown})")
        return "\n".join(lines)


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
            "Show a contact by name",
            "find-contact <name>",
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
            "update-contact <name>",
            handler.update_contact,
        ),
        (
            "delete-contact",
            "Delete a contact",
            "delete-contact <name>",
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


def _require_note_id(args: list[str], usage: str) -> UUID | str:
    """Parse a single note id, or return a usage message."""
    if len(args) != 1:
        return f"Usage: {usage}"
    try:
        return UUID(args[0])
    except ValueError:
        return "Note id must be a valid UUID."


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


def _format_contact(contact: Contact) -> str:
    phones = ", ".join(phone.value for phone in contact.phones) or "none"
    email = contact.email.value if contact.email else "none"
    birthday = contact.birthday.isoformat() if contact.birthday else "none"
    address = contact.address or "none"
    return (
        f"Name: {contact.name}\n"
        f"Address: {address}\n"
        f"Phones: {phones}\n"
        f"Email: {email}\n"
        f"Birthday: {birthday}"
    )


def _format_note(note: Note) -> str:
    tags = ", ".join(note.tags) or "none"
    content = note.content or "none"
    return f"Id: {note.id}\nTitle: {note.title}\nTags: {tags}\nContent: {content}"


__all__ = ["Command", "CommandHandler", "CommandRegistry", "build_registry"]
