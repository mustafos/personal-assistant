# Personal Assistant CLI

A command-line application for managing contacts, notes, tags, and birthday reminders. The application stores data locally in JSON files and automatically restores it between sessions.

## Features

### Contact Management

- Add, list, find, search, update, and delete contacts.
- Store contact names, phone numbers, email addresses, addresses, and birthdays.
- Identify contacts by UUID.
- Allow duplicate contact names.
- Search contacts by query.
- View upcoming birthdays within a specified number of days.

### Notes and Tags

- Create, list, find, search, update, and delete notes.
- Add multiple tags to notes.
- Remove tags from notes.
- Find notes by tag.
- Search notes by title or content.

### Data Persistence

- Store contacts and notes in JSON files.
- Automatically load saved data on application startup.
- Preserve data between application sessions.
- Allow users to specify a custom data directory.

### CLI

- Interactive command-line interface.
- Command-specific help.
- Input validation and usage instructions.
- Colored terminal output using Colorama.
- Graceful handling of invalid commands and missing arguments.
- Exit using `exit` or `quit`.

---

## Requirements

- **Python:** 3.12 or newer.
- **Colorama:** Used for colored terminal output.
- **Shlex:** Python standard library module used for command-line parsing. No separate installation is required.
- **Pytest:** Required for running tests.

---

## Installation and Startup

Clone the repository or navigate to the project directory.

### Windows

```cmd
cd /d C:\Users\Acer\personal-assistant
py -3.12 -m assistant.main
```

### Linux / macOS

```bash
cd personal-assistant
python3.12 -m assistant.main
```

The application starts in interactive mode and displays the available commands.

---

## Running Tests

Run the test suite using `pytest`:

### Windows

```cmd
py -3.12 -m pytest -v
```

### Linux / macOS

```bash
python3.12 -m pytest -v
```

---

## Data Storage

By default, application data is stored in the directory returned by `default_data_dir()`.

The application uses the following JSON files:

| File | Description |
|---|---|
| `contacts.json` | Stores contact records |
| `notes.json` | Stores notes and their tags |

All changes are saved to JSON files and loaded automatically the next time the application starts.

### Custom Data Directory

You can override the default storage location by setting the `PERSONAL_ASSISTANT_DATA_DIR` environment variable.

#### Windows

```cmd
set PERSONAL_ASSISTANT_DATA_DIR=C:\Users\Acer\personal-assistant\data
py -3.12 -m assistant.main
```

#### Linux / macOS

```bash
export PERSONAL_ASSISTANT_DATA_DIR="$PWD/data"
python3.12 -m assistant.main
```

This is useful for testing, development, or keeping application data in a specific directory.

---

## CLI Usage

The application uses an interactive command loop:

```text
read_line → command parsing → CommandHandler → services → storage → console output
```

The application continues running until the user enters `exit`, `quit`, or reaches the end of input.

### Command Input Rules

- Arguments must be provided directly in the command line.
- Values containing spaces must be enclosed in double quotes.
- Commands with missing or invalid arguments display usage instructions.
- Invalid input does not terminate the application.

Example:

```text
add-contact "Olena Koval" +380501112233 olena@example.com "Kyiv" 1998-11-27
```

---

## Available Commands

### Contacts and Birthdays

| Command | Description |
|---|---|
| `add-contact <name> [phone] [email] [address] [birthday]` | Creates a new contact. Birthday format: `YYYY-MM-DD`. |
| `list-contacts` | Displays all contacts and their details. |
| `find-contact <query>` | Finds a contact. |
| `search-contacts <query>` | Searches contacts using a query string. |
| `update-contact <id> <name\|phone\|email\|birthday> <value>` | Updates a contact field. |
| `delete-contact <id>` | Deletes a contact by ID. |
| `birthdays [days]` | Displays upcoming birthdays within the specified number of days. Defaults to 7 days. |

### Notes and Tags

| Command | Description |
|---|---|
| `add-note <title> [content] [tags]` | Creates a note. Tags can be comma-separated. |
| `list-notes` | Displays all notes. |
| `find-note <id>` | Finds a note by ID. |
| `search-notes <query>` | Searches notes by title or content. |
| `update-note <id> <field> <value>` | Updates a note field. |
| `delete-note <id>` | Deletes a note by ID. |
| `add-tag <id> <tag>` | Adds a tag to a note. |
| `remove-tag <id> <tag>` | Removes a tag from a note. |
| `notes-by-tag <tag>` | Displays notes containing the specified tag. |

### General Commands

| Command | Description |
|---|---|
| `help [command]` | Displays all commands or help for a specific command. |
| `exit` | Exits the application. |
| `quit` | Exits the application. |

---

## Examples

### Managing Contacts

```text
add-contact "Olena Koval" +380501112233 olena@example.com "Kyiv" 1998-11-27

list-contacts

search-contacts Olena

update-contact <contact_id> email olena.new@example.com

birthdays 7

delete-contact <contact_id>
```

### Managing Notes

```text
add-note "Release notes" "Initial draft" "work,release"

list-notes

notes-by-tag work

remove-tag <note_id> release

update-note <note_id> content "Final v1.0 ready"

search-notes Final

find-note <note_id>

delete-note <note_id>
```

### Persistence Between Sessions

Create a contact and exit the application:

```text
add-contact "Ada Lovelace" +442012345678 ada@example.com "London" 1815-12-10

exit
```

Restart the application:

```cmd
py -3.12 -m assistant.main
```

Then run:

```text
list-contacts
```

The previously saved contact will be loaded from the configured data directory.

---

## Project Structure

```text
personal-assistant/
├── assistant/
│   ├── main.py
│   ├── cli/
│   │   ├── commands.py
│   │   └── ...
│   ├── models/
│   │   ├── contact.py
│   │   ├── note.py
│   │   └── ...
│   ├── services/
│   │   ├── contact_service.py
│   │   ├── note_service.py
│   │   ├── birthday_service.py
│   │   └── ...
│   ├── storage/
│   │   ├── storage.py
│   │   ├── json_storage.py
│   │   └── ...
│   └── utils/
│       ├── validators.py
│       └── ...
├── tests/
├── pyproject.toml
└── README.md
```

---

## Architecture

The project follows a layered architecture:

```text
CLI
 │
 ▼
Command Handler
 │
 ▼
Services
 │
 ▼
Storage Abstraction
 │
 ▼
JSON Storage
```

- **CLI** — handles user input, command parsing, and console output.
- **Command Handler** — routes commands to the appropriate operations.
- **Services** — implement business logic for contacts, notes, tags, birthdays, and validation.
- **Storage Abstraction** — defines the interface for data persistence.
- **JSON Storage** — loads and saves records in JSON files.
- **Models** — represent contacts and notes and provide serialization methods.

`assistant.main` is responsible for initializing the application and wiring its dependencies.

Services receive a storage interface through dependency injection and should not depend directly on the JSON storage implementation.

---

## Data Models

Records are identified by UUIDs.

### Contact

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

### Note

```json
{
  "id": "2c0f1a4e-6b7d-4e5a-9c1d-0a1b2c3d4e5f",
  "title": "Lecture",
  "content": "Bring the notebook",
  "tags": ["school"]
}
```

Both models support:

- `to_dict()` — converts the model into a dictionary suitable for JSON serialization.
- `from_dict()` — restores a model from a dictionary.

### Data Rules

- IDs are UUID strings.
- Contact names do not have to be unique.
- Contact birthdays and emails may be `null`.
- Contact phone numbers and note tags may be empty lists.

---

## Development

Create a virtual environment:

### Windows

```cmd
py -3.12 -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install the project in editable mode:

```bash
python -m pip install -e .
```

If development dependencies are configured in `pyproject.toml`:

```bash
python -m pip install -e ".[dev]"
```

Integration happens on `develop`. Feature branches start from `develop`.
Read [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/onboarding.md](docs/onboarding.md)
before opening a branch.

| Issue | Scope | Modules |
| --- | --- | --- |
| #2 | Contact CRUD and birthday queries | `assistant/services/contact_service.py`, `assistant/services/birthday_service.py` |
| #3 | Note CRUD only | Note methods in `assistant/services/note_service.py`, except tag methods |
| #4 | JSON storage reliability and input validators | `assistant/storage/json_storage.py`, `assistant/utils/validators.py` |
| #5 | CLI and integration | `assistant/cli/` |
| #6 | Bonus: note tags, filtering, and sorting | Tag methods in `assistant/services/note_service.py` |

Birthday code stays in #2. Tag behavior stays in #6. Details are in
[docs/issue-scope.md](docs/issue-scope.md).

Keep the method signatures already documented on the service classes. Load and
save records through the injected `Storage` object, and match records by `id`.
`find-contact`, `update-contact`, and `delete-contact` take that id. Adding and
editing use the prompts in [docs/cli-contracts.md](docs/cli-contracts.md).

## Quality Checks

Run tests:

```bash
pytest -v
```

Run linting:

```bash
ruff check .
```

Check code formatting:

```bash
ruff format --check .
```

---

## License

Specify the project license here.
