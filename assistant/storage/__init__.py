"""Persistence abstractions and the JSON backend."""

from assistant.storage.json_storage import JSONStorage
from assistant.storage.storage import Storage, StorageError

__all__ = ["JSONStorage", "Storage", "StorageError"]
