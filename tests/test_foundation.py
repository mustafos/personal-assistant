"""Behavior tests for the application foundation."""

import tomllib
from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest

import assistant
from assistant.main import build_app, default_data_dir
from assistant.models.contact import Contact
from assistant.models.fields import EmailAddress, PhoneNumber
from assistant.models.note import Note
from assistant.services.birthday_service import BirthdayService
from assistant.services.contact_service import ContactService
from assistant.services.note_service import NoteService
from assistant.storage.json_storage import JSONStorage
from assistant.storage.storage import StorageError
from assistant.utils.helpers import normalize_whitespace, parse_iso_date
from assistant.utils.validators import is_valid_email, is_valid_phone

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_COMMANDS = (
    "add-contact",
    "list-contacts",
    "find-contact",
    "search-contacts",
    "update-contact",
    "delete-contact",
    "add-note",
    "list-notes",
    "find-note",
    "search-notes",
    "update-note",
    "delete-note",
    "add-tag",
    "remove-tag",
    "notes-by-tag",
    "birthdays",
    "help",
    "exit",
)


def _run(tmp_path: Path, lines: list[str]) -> str:
    incoming = iter(lines)

    def read_line(_prompt: str) -> str:
        return next(incoming)

    messages: list[str] = []
    cli = build_app(tmp_path, input_func=read_line, output_func=messages.append)
    cli.run()
    return "\n".join(messages)


def test_package_metadata_matches_project_config() -> None:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]

    assert project["name"] == "personal-assistant"
    assert project["version"] == assistant.__version__
    assert project["requires-python"] == ">=3.12"
    assert project["dependencies"] == []
    assert project["scripts"]["personal-assistant"] == "assistant.main:main"


def test_contact_normalizes_fields_and_round_trips() -> None:
    contact = Contact(
        name="  Ada   Lovelace ",
        address="  London  ",
        phones=[PhoneNumber(" +44 20 ")],
        email=EmailAddress(" ada@example.com "),
        birthday=date(1815, 12, 10),
    )

    assert contact.name == "Ada Lovelace"
    assert contact.address == "London"
    assert contact.phones[0].value == "+44 20"
    assert contact.email is not None
    assert contact.email.value == "ada@example.com"
    restored = Contact.from_dict(contact.to_dict())
    assert restored == contact
    assert restored.id == contact.id
    assert contact.to_dict()["id"] == str(contact.id)


def test_contact_rejects_blank_name() -> None:
    with pytest.raises(ValueError):
        Contact(name="   ")


def test_contacts_may_share_a_name() -> None:
    first = Contact(name="Ada Lovelace")
    second = Contact(name="Ada Lovelace")

    assert first.name == second.name
    assert first.id != second.id
    assert Contact.from_dict(first.to_dict()).id == first.id


def test_note_round_trip_keeps_id_and_tags() -> None:
    note_id = uuid4()
    note = Note(
        title="  Shopping   list ",
        content="  Milk\nBread  ",
        tags=[" errands ", "home"],
        id=note_id,
    )

    assert note.id == note_id
    assert note.title == "Shopping list"
    assert note.content == "Milk\nBread"
    assert note.tags == ["errands", "home"]
    assert Note.from_dict(note.to_dict()) == note


def test_notes_receive_unique_ids() -> None:
    assert Note(title="One").id != Note(title="Two").id


def test_field_values_reject_blank_text() -> None:
    with pytest.raises(ValueError):
        PhoneNumber("   ")
    with pytest.raises(ValueError):
        EmailAddress("   ")


def test_json_storage_round_trip(tmp_path: Path) -> None:
    storage = JSONStorage(tmp_path / "nested" / "contacts.json")

    assert storage.load() == []
    assert not storage.path.exists()

    contact = Contact(name="Ada Lovelace", birthday=date(1815, 12, 10))
    storage.save([contact.to_dict()])

    loaded = Contact.from_dict(storage.load()[0])
    assert loaded == contact
    assert storage.path.read_text(encoding="utf-8").endswith("\n")


def test_json_storage_rejects_invalid_documents(tmp_path: Path) -> None:
    storage = JSONStorage(tmp_path / "contacts.json")
    storage.path.write_text("{", encoding="utf-8")
    with pytest.raises(StorageError):
        storage.load()

    storage.path.write_text('{"name": "Ada"}', encoding="utf-8")
    with pytest.raises(StorageError):
        storage.load()

    with pytest.raises(TypeError):
        storage.save(["not-an-object"])


def test_blank_storage_file_loads_as_empty(tmp_path: Path) -> None:
    storage = JSONStorage(tmp_path / "notes.json")
    storage.path.write_text(" \n", encoding="utf-8")
    assert storage.load() == []


def test_note_service_is_not_implemented_yet(tmp_path: Path) -> None:
    contact_storage = JSONStorage(tmp_path / "contacts.json")
    note_storage = JSONStorage(tmp_path / "notes.json")
    birthdays = BirthdayService(ContactService(contact_storage))
    notes = NoteService(note_storage)

    with pytest.raises(NotImplementedError):
        notes.find_by_tag("school")
    with pytest.raises(ValueError):
        birthdays.upcoming_birthdays(-1)

    assert not contact_storage.path.exists()
    assert not note_storage.path.exists()


def test_validation_rules_are_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        is_valid_phone("+44 20")
    with pytest.raises(NotImplementedError):
        is_valid_email("ada@example.com")


def test_helpers() -> None:
    assert normalize_whitespace("  a   b ") == "a b"
    assert parse_iso_date("1815-12-10") == date(1815, 12, 10)


def test_cli_welcome_lists_commands_and_exits(tmp_path: Path) -> None:
    output = _run(tmp_path, ["exit"])

    assert output.startswith("Personal Assistant")
    assert "Manage contacts, notes, and birthday reminders." in output
    for command in EXPECTED_COMMANDS:
        assert command in output
    assert output.endswith("Goodbye.")
    assert not (tmp_path / "contacts.json").exists()
    assert not (tmp_path / "notes.json").exists()


def test_cli_help_usage_and_unknown_command(tmp_path: Path) -> None:
    output = _run(tmp_path, ["help add-contact", "nope", "quit"])

    assert "Usage: add-contact <name>" in output
    assert "Unknown command: 'nope'" in output
    assert output.endswith("Goodbye.")


def test_cli_reports_unimplemented_commands(tmp_path: Path) -> None:
    output = _run(
        tmp_path,
        ["add-contact Ada Lovelace", "add-contact", "birthdays", "exit"],
    )

    assert output.count("This command is not implemented yet.") == 2
    assert "Usage: add-contact <name>" in output


def test_cli_exits_on_end_of_input(tmp_path: Path) -> None:
    def read_line(_prompt: str) -> str:
        raise EOFError

    messages: list[str] = []
    cli = build_app(tmp_path, input_func=read_line, output_func=messages.append)
    cli.run()

    text = "\n".join(messages)
    assert "Personal Assistant" in text
    assert text.endswith("Goodbye.")


def test_default_output_prints_welcome(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    cli = build_app(tmp_path, input_func=lambda _prompt: "exit")
    cli.run()

    captured = capsys.readouterr()
    assert "Personal Assistant" in captured.out
    assert "Goodbye." in captured.out
    assert captured.err == ""


def test_data_dir_can_be_overridden(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PERSONAL_ASSISTANT_DATA_DIR", str(tmp_path))
    assert default_data_dir() == tmp_path
