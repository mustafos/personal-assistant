"""End-to-end workflow tests for the Personal Assistant CLI."""

from datetime import date, timedelta
from pathlib import Path

from assistant.main import build_app


def _run_session(tmp_path: Path, commands: list[str]) -> list[str]:
    incoming = iter(commands)

    def read_line(_prompt: str) -> str:
        return next(incoming)

    messages: list[str] = []
    cli = build_app(tmp_path, input_func=read_line, output_func=messages.append)
    cli.run()
    return messages


def _extract_id(lines: list[str], prefix: str) -> str:
    matched = next(line for line in lines if line.startswith(prefix))
    return matched.split("id=", 1)[1].split(" | ", 1)[0].strip()


def test_end_to_end_contacts_notes_tags_birthdays_update_and_restart(
    tmp_path: Path,
) -> None:
    upcoming = date.today() + timedelta(days=2)
    birthday_str = f"1998-{upcoming.month:02d}-{upcoming.day:02d}"

    session_1 = _run_session(
        tmp_path,
        [
            'add-contact "Olena Koval" +380501112233 '
            f'olena@example.com "Kyiv" {birthday_str}',
            "list-contacts",
            "birthdays 7",
            "exit",
        ],
    )
    text_1 = "\n".join(session_1)
    assert "Contact added:" in text_1
    assert "Olena Koval" in text_1
    assert "No upcoming birthdays within 7 days." not in text_1
    contact_id = _extract_id(session_1, "Contact added:")

    session_2 = _run_session(
        tmp_path,
        [
            'add-note "Release notes" "Initial draft" "work,release"',
            "notes-by-tag work",
            "exit",
        ],
    )
    text_2 = "\n".join(session_2)
    assert "Note added:" in text_2
    assert "Release notes" in text_2
    note_id = _extract_id(session_2, "Note added:")

    session_3 = _run_session(
        tmp_path,
        [
            f"update-contact {contact_id} email olena.new@example.com",
            f"remove-tag {note_id} release",
            f'update-note {note_id} content "Final v1.0 ready"',
            f"find-note {note_id}",
            "search-notes Final",
            "exit",
        ],
    )
    text_3 = "\n".join(session_3)
    assert "olena.new@example.com" in text_3
    assert "content=Final v1.0 ready" in text_3
    assert "tags=[work]" in text_3

    session_4 = _run_session(
        tmp_path,
        [
            "list-contacts",
            "birthdays 7",
            "search-notes Final",
            "exit",
        ],
    )
    text_4 = "\n".join(session_4)
    assert "Olena Koval" in text_4
    assert "olena.new@example.com" in text_4
    assert "content=Final v1.0 ready" in text_4
    assert "No upcoming birthdays within 7 days." not in text_4


def test_invalid_commands_and_malformed_input_do_not_crash(tmp_path: Path) -> None:
    missing_id = "00000000-0000-0000-0000-000000000000"
    outputs = _run_session(
        tmp_path,
        [
            "unknown-command arg1",
            "find-note not-a-valid-uuid",
            f"find-note {missing_id}",
            f"update-contact {missing_id} email a@b.com",
            f"remove-tag {missing_id} work",
            "notes-by-tag nonexistent-tag",
            'add-note "Unclosed title "missing end quote',
            "exit",
        ],
    )
    text = "\n".join(outputs)
    assert "Unknown command: 'unknown-command'" in text
    assert text.endswith("Goodbye.")
