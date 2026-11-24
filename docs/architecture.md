# Architecture

The application is a command-line assistant. Business operations are not
implemented yet. The classes and method signatures below are the contract.

```text
CLI -> services -> Storage
models are used by services
JSONStorage is constructed only in assistant/main.py
```

## Layers

| Layer | Path | Responsibility |
| --- | --- | --- |
| CLI | `assistant/cli/` | Read a line, check its shape, call a service, print the result |
| Services | `assistant/services/` | Contacts, notes, and birthday queries |
| Storage | `assistant/storage/` | Save and load one list of dictionaries |
| Models | `assistant/models/` | `Contact`, `Note`, `PhoneNumber`, `EmailAddress` |
| Utils | `assistant/utils/` | Shared text helpers and phone/email validators |

Models do not import the CLI, services, or storage. Service modules do not
import `json` or `JSONStorage`. The CLI does not import `JSONStorage`.

## Models

`Contact.id` and `Note.id` are UUIDs created with `uuid4` when the caller does
not pass one. A name or title does not identify a record. Two contacts may
share a name.

`Contact` fields: `id`, `name`, `address`, `phones`, `email`, `birthday`.
`address` defaults to `""`. `email` and `birthday` may be `None`. `phones` is
a list of `PhoneNumber`.

`Note` fields: `id`, `title`, `content`, `tags`. `content` defaults to `""`.
`tags` is a list of strings.

Both models implement `to_dict()` and `from_dict()`. `id` is stored as a UUID
string. `birthday` is `YYYY-MM-DD` or `null`.

`PhoneNumber` and `EmailAddress` store trimmed text. Format rules belong in
`assistant/utils/validators.py`, which is not implemented yet.

## Services

Persistence uses the injected `Storage`:

```python
records = self._storage.load()
contacts = [Contact.from_dict(record) for record in records]
self._storage.save([contact.to_dict() for contact in contacts])
```

Match an existing record by `id`.

### ContactService

```text
add_contact(contact: Contact) -> None
get_contact(contact_id: UUID) -> Contact | None
list_contacts() -> list[Contact]
search_contacts(query: str) -> list[Contact]
update_contact(contact: Contact) -> None
delete_contact(contact_id: UUID) -> None
```

`add_contact` raises `ValueError` when that `id` is already stored.
`update_contact` and `delete_contact` raise `LookupError` when the `id` is
unknown. `get_contact` returns `None` in that case.
`update_contact` replaces the stored contact that has `contact.id`.
Search is case-insensitive across name, address, phones, and email. Stored
capitalization is kept.

### NoteService

```text
add_note(note: Note) -> None
get_note(note_id: UUID) -> Note | None
list_notes() -> list[Note]
search_notes(query: str) -> list[Note]
update_note(note: Note) -> None
delete_note(note_id: UUID) -> None
add_tag(note_id: UUID, tag: str) -> None
remove_tag(note_id: UUID, tag: str) -> None
find_by_tag(tag: str) -> list[Note]
```

CRUD follows the same id rules as contacts. Search is case-insensitive across
title, content, and tags.

`add_tag`, `remove_tag`, and `find_by_tag` are the bonus tag interface. Issue
#3 does not implement them. Adding a tag that is already present, and removing
a tag that is absent, leave the note unchanged. Tag comparison is
case-insensitive. An empty tag raises `ValueError`.

### BirthdayService

```text
upcoming_birthdays(within_days: int) -> list[Contact]
```

The service receives `ContactService` and reads contacts with
`list_contacts()`. It does not open a file. The window starts today and
includes the day `within_days` days ahead. `0` means today only. A negative
value raises `ValueError`. A non-integer raises `TypeError`. Contacts with
`birthday is None` are skipped. What to do with 29 February is not defined.

The CLI calls this with `7` when the user omits the day count.

## Storage

```text
save(records: list[dict]) -> None
load() -> list[dict]
```

`load()` returns `[]` when the file is missing or blank. Corrupt JSON, or a
JSON value that is not a list of objects, raises `StorageError`.

`assistant/main.py` creates two files in the project `data/` directory:

- `data/contacts.json`
- `data/notes.json`

`PERSONAL_ASSISTANT_DATA_DIR` overrides that directory. Files are created only
when a service saves. `data/` is gitignored.

## CLI

`assistant/cli/interface.py` prints the command list, reads lines, and exits on
`exit`, `quit`, or end of input. `help` and `help <command>` are handled there.

`assistant/cli/commands.py` registers commands and checks argument shape.
Handlers do not call the services yet. When they do, they must follow
[cli-contracts.md](cli-contracts.md).

`NotImplementedError` is printed as "This command is not implemented yet."
`LookupError`, `ValueError`, and `StorageError` are printed and the loop
continues.
