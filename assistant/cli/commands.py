"""CLI command definitions.

Commands are registered here. Handlers validate the command line and call
the injected services.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from assistant.models.contact import Contact
from assistant.models.fields import EmailAddress, PhoneNumber, normalize_label
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


def _parse_birthday(raw: str) -> date:
    """Parse the date of birth in the YYYY-MM-DD format."""
    return date.fromisoformat(raw.strip())


def _format_contact(contact: Contact) -> str:
    """Create a text string with the contact's data for the console."""
    phones = ", ".join(p.value for p in contact.phones) if contact.phones else "-"
    email = contact.email.value if contact.email else "-"
    address = contact.address if contact.address else "-"
    birthday = contact.birthday.isoformat() if contact.birthday else "-"
    return (
        f"id={contact.id} | name={contact.name} | phones={phones} | "
        f"email={email} | address={address} | birthday={birthday}"
    )


def _format_note(note: Note) -> str:
    tags = ", ".join(note.tags) if note.tags else "-"
    content = note.content if note.content else "-"
    return f"id={note.id} | title={note.title} | content={content} | tags=[{tags}]"


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
        """Add a contact: add-contact <name> [phone] [email] [address] [birthday]."""
        if not args:
            return "Usage: add-contact <name> [phone] [email] [address] [birthday]"

        name = normalize_whitespace(args[0])
        if not name:
            return "Usage: add-contact <name> [phone] [email] [address] [birthday]"

        phones: list[PhoneNumber] = []
        if len(args) >= 2 and args[1].strip():
            phones.append(PhoneNumber(args[1]))

        email: EmailAddress | None = None
        if len(args) >= 3 and args[2].strip():
            email = EmailAddress(args[2])

        address = normalize_whitespace(args[3]) if len(args) >= 4 else ""

        birthday: date | None = None
        if len(args) >= 5 and args[4].strip():
            birthday = _parse_birthday(args[4])

        contact = Contact(
            name=name,
            address=address,
            phones=phones,
            email=email,
            birthday=birthday,
        )

        self._contacts.add_contact(contact)
        return f"Contact added: {_format_contact(contact)}"

    def list_contacts(self, args: list[str]) -> str:
        """Displays all contacts: list-contacts."""
        if args:
            return "Usage: list-contacts"

        contacts = self._contacts.list_contacts()
        if not contacts:
            return "No contacts found."

        return "\n".join(_format_contact(contact) for contact in contacts)

    def find_contact(self, args: list[str]) -> str:
        """Finds a contact by UUID and shows their card: find-contact <id>."""
        parsed = _require_id(args, "find-contact <id>")
        if isinstance(parsed, str):
            return parsed
        contact = self._contacts.get_contact(parsed)
        if contact is None:
            raise LookupError(f"Contact not found: {parsed}")

        return _format_contact(contact)

    def search_contacts(self, args: list[str]) -> str:
        """Searching for contacts by text query: search-contacts <query>."""
        query = _require_text(args)
        if query is None:
            return "Usage: search-contacts <query>"

        matches = self._contacts.search_contacts(query)
        if not matches:
            return f"No contacts matching '{query}'."

        return "\n".join(_format_contact(contact) for contact in matches)

    def update_contact(self, args: list[str]) -> str:
        """Update one contact field by UUID."""
        if len(args) < 3:
            return (
                "Usage: update-contact <id> <name|phone|email|address|birthday> <value>"
            )

        try:
            contact_id = UUID(args[0])
        except ValueError:
            return "Id must be a valid UUID."

        field_name = args[1].casefold()
        raw_value = " ".join(args[2:])
        if not raw_value.strip():
            return "Usage: update-contact <id> <name|phone|email|birthday> <value>"

        current = self._contacts.get_contact(contact_id)
        if current is None:
            raise LookupError(f"Contact not found: {contact_id}")

        name = current.name
        address = current.address
        phones = list(current.phones)
        email = current.email
        birthday = current.birthday
        is_clear = raw_value.strip().casefold() == "clear"

        if field_name == "name":
            name = normalize_whitespace(raw_value)
        elif field_name == "address":
            address = "" if is_clear else normalize_whitespace(raw_value)
        elif field_name == "phone":
            phones = [] if is_clear else [PhoneNumber(raw_value)]
        elif field_name == "email":
            email = None if is_clear else EmailAddress(raw_value)
        elif field_name == "birthday":
            birthday = None if is_clear else _parse_birthday(raw_value)
        else:
            return "Usage: update-contact <id> <name|phone|email|birthday> <value>"

        updated = Contact(
            name=name,
            address=address,
            phones=phones,
            email=email,
            birthday=birthday,
            id=current.id,
        )

        self._contacts.update_contact(updated)
        return f"Contact updated: {_format_contact(updated)}"

    def delete_contact(self, args: list[str]) -> str:
        """Removes a contact by UUID: delete-contact <id>."""
        parsed = _require_id(args, "delete-contact <id>")
        if isinstance(parsed, str):
            return parsed

        self._contacts.delete_contact(parsed)
        return f"Contact deleted: {parsed}"

    def add_note(self, args: list[str]) -> str:
        """Adds a note: add-note <title> [content] [tags]."""
        if not args:
            return "Usage: add-note <title> [content] [tags]"

        title = args[0]
        if not normalize_whitespace(title):
            return "Usage: add-note <title> [content] [tags]"

        content = args[1] if len(args) >= 2 else ""

        tags: list[str] = []
        if len(args) >= 3 and args[2].strip():
            raw_tags = args[2:] if len(args) > 3 else args[2].split(",")
            for part in raw_tags:
                cleaned_tag = normalize_label(part, field_name="Tag")
                if all(
                    existing.casefold() != cleaned_tag.casefold() for existing in tags
                ):
                    tags.append(cleaned_tag)

        note = Note(
            title=title,
            content=content,
            tags=tags,
        )

        self._notes.add_note(note)
        return f"Note added: {_format_note(note)}"

    def list_notes(self, args: list[str]) -> str:
        "Displays all notes: list-notes."
        if args:
            return "Usage: list-notes"

        notes = self._notes.list_notes()
        if not notes:
            return "No notes found."

        return "\n".join(_format_note(note) for note in notes)

    def find_note(self, args: list[str]) -> str:
        """Finds a note by UUID and displays its card: find-note <id>."""
        parsed = _require_id(args, "find-note <id>")
        if isinstance(parsed, str):
            return parsed

        note = self._notes.get_note(parsed)
        if note is None:
            raise LookupError(f"Note not found: {parsed}")

        return _format_note(note)

    def search_notes(self, args: list[str]) -> str:
        """Looking for notes by text query: search-notes <query>."""
        query = _require_text(args)
        if query is None:
            return "Usage: search-notes <query>"

        matches = self._notes.search_notes(query)
        if not matches:
            return f"No notes matching '{query}'."

        return "\n".join(_format_note(note) for note in matches)

    def update_note(self, args: list[str]) -> str:
        """Update one note field by UUID."""
        if len(args) < 3:
            return "Usage: update-note <id> <title|content|tags> <value>"

        try:
            note_id = UUID(args[0])
        except ValueError:
            return "Id must be a valid UUID."

        field_name = args[1].casefold()
        raw_value = " ".join(args[2:])
        if not raw_value.strip() and field_name != "content":
            return "Usage: update-note <id> <title|content|tags> <value>"

        current = self._notes.get_note(note_id)
        if current is None:
            raise LookupError(f"Note not found: {note_id}")

        title = current.title
        content = current.content
        tags = list(current.tags)

        if field_name == "title":
            if not normalize_whitespace(raw_value):
                return "Usage: update-note <id> <title|content|tags> <value>"
            title = raw_value
        elif field_name == "content":
            content = raw_value
        elif field_name == "tags":
            new_tags: list[str] = []
            for part in raw_value.split(","):
                if part.strip():
                    cleaned_tag = normalize_label(part, field_name="Tag")
                    if all(
                        existing.casefold() != cleaned_tag.casefold()
                        for existing in new_tags
                    ):
                        new_tags.append(cleaned_tag)
            tags = new_tags
        else:
            return "Usage: update-note <id> <title|content|tags> <value>"

        updated = Note(
            title=title,
            content=content,
            tags=tags,
            id=current.id,
        )
        self._notes.update_note(updated)

        return f"Note updated: {_format_note(updated)}"

    def delete_note(self, args: list[str]) -> str:
        """Deletes a note by UUID: delete-note <id>."""
        parsed = _require_id(args, "delete-note <id>")
        if isinstance(parsed, str):
            return parsed
        self._notes.delete_note(parsed)
        return f"Note deleted: {parsed}"

    def add_tag(self, args: list[str]) -> str:
        """Adds a tag to a note by UUID: add-tag <note-id> <tag>."""
        parsed = _note_id_and_tag(args, "add-tag <note-id> <tag>")
        if isinstance(parsed, str):
            return parsed

        note_id, raw_tag = parsed
        tag = normalize_label(raw_tag, field_name="Tag")
        self._notes.add_tag(note_id, tag)

        updated = self._notes.get_note(note_id)
        if updated is None:
            raise LookupError(f"Note not found: {note_id}")
        return f"Tag '{tag}' added: {_format_note(updated)}"

    def remove_tag(self, args: list[str]) -> str:
        """Removes a tag from a note by UUID: remove-tag <note-id> <tag>."""
        parsed = _note_id_and_tag(args, "remove-tag <note-id> <tag>")
        if isinstance(parsed, str):
            return parsed

        note_id, raw_tag = parsed
        tag = normalize_label(raw_tag, field_name="Tag")
        self._notes.remove_tag(note_id, tag)

        updated = self._notes.get_note(note_id)
        if updated is None:
            raise LookupError(f"Note not found: {note_id}")
        return f"Tag '{tag}' removed: {_format_note(updated)}"

    def notes_by_tag(self, args: list[str]) -> str:
        """Displays notes by tag, sorted by tags: notes-by-tag <tag>."""
        raw_tag = _require_text(args)
        if raw_tag is None:
            return "Usage: notes-by-tag <tag>"

        tag = normalize_label(raw_tag, field_name="Tag")
        notes = self._notes.find_by_tag(tag)
        if not notes:
            return f"No notes with tag '{tag}'."

        return "\n".join(_format_note(note) for note in notes)

    def birthdays(self, args: list[str]) -> str:
        """Displays contacts with upcoming birthdays: birthdays [days]."""
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

        upcoming = self._birthdays.upcoming_birthdays(days)
        if not upcoming:
            return f"No upcoming birthdays within {days} days."

        return "\n".join(_format_contact(contact) for contact in upcoming)


def build_registry(handler: CommandHandler) -> CommandRegistry:
    """Register the contact, note, and birthday commands.

    Args:
        handler: Object that implements the command methods.

    Returns:
        A registry in display order.
    """
    specs: tuple[tuple[str, str, str, Callable[[list[str]], str]], ...] = (
        (
            "add-contact",
            "Add a contact",
            "add-contact <name> [phone] [email] [address] [birthday]",
            handler.add_contact,
        ),
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
            "update-contact <id> <name|phone|email|address|birthday> <value>",
            handler.update_contact,
        ),
        (
            "delete-contact",
            "Delete a contact",
            "delete-contact <id>",
            handler.delete_contact,
        ),
        (
            "add-note",
            "Add a note",
            "add-note <title> [content] [tags]",
            handler.add_note,
        ),
        ("list-notes", "List all notes", "list-notes", handler.list_notes),
        ("find-note", "Show a note by id", "find-note <id>", handler.find_note),
        ("search-notes", "Search notes", "search-notes <query>", handler.search_notes),
        (
            "update-note",
            "Update a note",
            "update-note <id> <title|content|tags> <value>",
            handler.update_note,
        ),
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
