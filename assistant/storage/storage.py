"""Storage contract shared by contacts and notes."""

from abc import ABC, abstractmethod
from typing import Any


class StorageError(Exception):
    """Raised when a storage backend cannot read or write data."""


class Storage(ABC):
    """Persistence for one collection of JSON-ready records.

    A record is a dictionary produced by a model's ``to_dict`` method.
    One storage instance holds one collection, so contacts and notes use
    separate instances. Services depend on this class and receive a concrete
    backend from ``assistant.main``.
    """

    @abstractmethod
    def save(self, records: list[dict[str, Any]]) -> None:
        """Replace the stored collection with ``records``.

        Args:
            records: JSON-ready mappings. The previous contents are discarded.

        Raises:
            StorageError: If the collection cannot be written.
        """

    @abstractmethod
    def load(self) -> list[dict[str, Any]]:
        """Return the stored collection.

        Returns:
            The saved records. An empty list means nothing has been stored.

        Raises:
            StorageError: If the stored data cannot be read.
        """


__all__ = ["Storage", "StorageError"]
