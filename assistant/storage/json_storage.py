"""JSON file implementation of the storage contract."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from assistant.storage.storage import Storage, StorageError


class JSONStorage(Storage):
    """Store one collection as a JSON list in a single file.

    A missing file loads as an empty collection. Saving creates parent
    directories when needed and rewrites the whole file.
    """

    def __init__(self, path: str | Path) -> None:
        """Point this backend at ``path``.

        Args:
            path: File that will hold the JSON list. It is not created until
                :meth:`save` is called.
        """
        self._path = Path(path)

    @property
    def path(self) -> Path:
        """Filesystem location of the JSON file."""
        return self._path

    def save(self, records: list[dict[str, Any]]) -> None:
        """Write ``records`` as indented UTF-8 JSON.

        Args:
            records: JSON-ready mappings that replace the current file.

        Raises:
            TypeError: If ``records`` is not a list.
            StorageError: If the payload cannot be encoded or written.
        """
        if not isinstance(records, list):
            raise TypeError("Records must be a list.")
        if any(not isinstance(record, dict) for record in records):
            raise TypeError("Each record must be a dictionary.")
        try:
            payload = json.dumps(records, indent=2, ensure_ascii=False) + "\n"
        except TypeError as exc:
            raise StorageError(f"Could not encode JSON for {self._path}.") from exc
        try:
            tmp_name = None
            self._path.parent.mkdir(parents=True, exist_ok=True)
            tmp_fd, tmp_name = tempfile.mkstemp(dir=self._path.parent)
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as tmp_file:
                tmp_file.write(payload)
            os.replace(tmp_name, self._path)

        except OSError as exc:
            if tmp_name is not None:
                try:
                    os.unlink(tmp_name)
                except OSError:
                    pass
            raise StorageError(f"Could not write {self._path}.") from exc

    def load(self) -> list[dict[str, Any]]:
        """Read the JSON list from disk.

        Returns:
            Stored objects, or an empty list when the file is missing or blank.

        Raises:
            StorageError: If the file cannot be read or is not a list of objects.
        """
        if not self._path.exists():
            return []
        try:
            raw = self._path.read_text(encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Could not read {self._path}.") from exc
        if not raw.strip():
            return []
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise StorageError(f"Invalid JSON in {self._path}.") from exc
        if not isinstance(data, list) or any(
            not isinstance(item, dict) for item in data
        ):
            raise StorageError(f"Expected a JSON list of objects in {self._path}.")
        return [dict(item) for item in data]


__all__ = ["JSONStorage"]
