"""Application entry point.

This module is the composition root. It creates storage, services, and the
CLI, then starts the interactive loop.
"""

import os
import sys
from collections.abc import Callable
from pathlib import Path

from assistant.cli.commands import CommandHandler, build_registry
from assistant.cli.interface import CLI
from assistant.services.birthday_service import BirthdayService
from assistant.services.contact_service import ContactService
from assistant.services.note_service import NoteService
from assistant.storage.json_storage import JSONStorage

CONTACTS_FILE = "contacts.json"
NOTES_FILE = "notes.json"
DEFAULT_DATA_DIR = Path("data")
DATA_DIR_ENV = "PERSONAL_ASSISTANT_DATA_DIR"


def default_data_dir() -> Path:
    """Return the directory used for JSON data files.

    The default is ``data`` in the current working directory. Set
    ``PERSONAL_ASSISTANT_DATA_DIR`` to use another directory.
    """
    override = os.environ.get(DATA_DIR_ENV)
    if override:
        return Path(override)
    return DEFAULT_DATA_DIR


def build_app(
    data_dir: Path | None = None,
    *,
    input_func: Callable[[str], str] | None = None,
    output_func: Callable[[str], None] | None = None,
) -> CLI:
    """Create the CLI with storage and services connected.

    Args:
        data_dir: Directory for ``contacts.json`` and ``notes.json``.
            Defaults to :func:`default_data_dir`.
        input_func: Line reader. Defaults to :func:`input`.
        output_func: Line writer. Defaults to :func:`print`.

    Returns:
        A CLI ready to run. Storage files are created only when a service
        saves data.
    """
    root = default_data_dir() if data_dir is None else Path(data_dir)
    contact_service = ContactService(JSONStorage(root / CONTACTS_FILE))
    note_service = NoteService(JSONStorage(root / NOTES_FILE))
    birthday_service = BirthdayService(contact_service)
    handler = CommandHandler(contact_service, note_service, birthday_service)
    return CLI(
        build_registry(handler),
        input_func=input_func,
        output_func=output_func,
    )


def main() -> None:
    """Start the Personal Assistant command-line interface."""
    try:
        build_app().run()
    except KeyboardInterrupt:
        print("\nGoodbye.")
    except OSError as exc:
        print(f"Could not start the application: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
