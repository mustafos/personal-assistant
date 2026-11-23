# Personal Assistant

Command-line application for storing contacts and notes on the local machine.
The project is a course foundation: the packages, models, storage contract, and
command loop are in place so team members can implement features independently.

Business operations such as saving a contact, searching notes, calculating
birthdays, and validating phone numbers or email addresses are not implemented
yet. Calling them raises `NotImplementedError`.

## Features

The finished application is intended to provide:

- Contact management: add, list, find, search, update, and delete contacts.
- Note management: add, list, find, search, update, and delete notes.
- Tags on notes.
- Birthday reminders for a chosen number of days.
- Reusable phone and email validation.
- Local JSON files for contacts and notes.

Current status:

- Models can be created and converted to dictionaries.
- `JSONStorage` can load and save a JSON list.
- Service methods define the contracts and still need their implementations.
- Contacts and notes are identified by UUID. Contact names may be repeated.
- The CLI starts, lists commands, checks basic command shape, and exits.
- Contact and note commands are registered scaffolds.
- Phone and email validators are reserved function names.

## Project structure

```text
personal-assistant/
├── assistant/
│   ├── main.py                 # wires storage, services, and the CLI
│   ├── cli/                    # input loop and command parsing
│   ├── models/                 # Contact, Note, and field values
│   ├── services/               # business-operation interfaces
│   ├── storage/                # Storage abstraction and JSON backend
│   └── utils/                  # helpers and validators
├── tests/
├── pyproject.toml
└── README.md
```

Dependency direction:

```text
CLI -> services -> storage abstraction
models are used by services and may be serialized by storage callers
```

`assistant.main` is the only place that constructs `JSONStorage`. Services
receive a `Storage` object and should not import the JSON backend.

## Record format

`data/contacts.json` and `data/notes.json` are lists of objects. Service
authors should build those objects with `Contact.to_dict()` and
`Note.to_dict()`, and restore them with `from_dict()`.

Contact:

```json
{
  "id": "6f1c2a90-1b2e-4d55-9a0c-7e8f6a5b4c3d",
  "name": "Ada Lovelace",
  "address": "London",
  "phones": ["+44 20 7946 0991"],
  "email": "ada@example.com",
  "birthday": "1815-12-10"
}
```

Note:

```json
{
  "id": "2c0f1a4e-6b7d-4e5a-9c1d-0a1b2c3d4e5f",
  "title": "Lecture",
  "content": "Bring the notebook",
  "tags": ["school"]
}
```

Both models use `to_dict()` and `from_dict()`. `id` is a UUID string and is the
only identity of a record. A contact name does not have to be unique.
`birthday` and `email` may be `null`. `phones` and `tags` may be empty lists.

## Installation

Requires Python 3.12 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

On Windows, activate the environment with `.venv\Scripts\activate`.

The editable install creates the `personal-assistant` command.

## Development setup

Install the test and lint tools together with the package:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Suggested split for parallel work:

| Area | Modules |
| --- | --- |
| Contacts | `assistant/services/contact_service.py` |
| Notes and tags | `assistant/services/note_service.py` |
| Birthdays | `assistant/services/birthday_service.py` |
| Validation | `assistant/utils/validators.py` |
| Command editing flow | `assistant/cli/commands.py` |

Keep the method signatures already documented on the service classes. Load and
save records through the injected `Storage` object, and match records by `id`.
`find-contact`, `update-contact`, and `delete-contact` take that id.

## Startup

From the project directory, after installation:

```bash
personal-assistant
```

Without installing the console script:

```bash
python -m assistant.main
```

The program prints a welcome message and the command list. Type `help` to show
it again, `help add-contact` to show one command, and `exit` or `quit` to
leave. End-of-input also exits.

Data files are created only when a future service saves records:

- `data/contacts.json`
- `data/notes.json`

Set `PERSONAL_ASSISTANT_DATA_DIR` to store those files somewhere else.

Data commands check their argument shape, then report that the command is not
implemented yet.

## Testing

With the development tools installed:

```bash
pytest
ruff check .
ruff format --check .
```
