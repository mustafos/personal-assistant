"""Business operations for contacts."""

from assistant.models.contact import Contact
from assistant.storage.storage import Storage


class ContactService:
    """Create, read, search, update, and delete contacts.

    Pass a :class:`~assistant.storage.storage.Storage` instance. This class
    must not open files or import the JSON backend. An implementation should
    load records, convert them with :meth:`Contact.from_dict`, change the
    list, and save ``contact.to_dict()`` mappings through the same storage.

    Name comparisons are case-insensitive. Stored capitalization is kept.
    Each method raises ``NotImplementedError`` until it is implemented.
    Other exceptions named on a method describe the contract the
    implementation must follow.
    """

    def __init__(self, storage: Storage) -> None:
        """Store the persistence dependency.

        Args:
            storage: Backend for the contact collection.
        """
        self._storage = storage

    def add_contact(self, contact: Contact) -> None:
        """Store a new contact.

        Args:
            contact: Contact to add.

        Raises:
            NotImplementedError: Saving contacts is not implemented yet.
            ValueError: If a contact with the same name already exists.
        """
        raise NotImplementedError("ContactService.add_contact is not implemented yet.")

    def get_contact(self, name: str) -> Contact | None:
        """Return the contact named ``name``.

        Args:
            name: Contact name. Lookup ignores case and extra whitespace.

        Returns:
            The stored contact, or None when no name matches.

        Raises:
            NotImplementedError: Contact lookup is not implemented yet.
        """
        raise NotImplementedError("ContactService.get_contact is not implemented yet.")

    def list_contacts(self) -> list[Contact]:
        """Return every stored contact.

        Returns:
            All contacts. The order matches the stored collection.

        Raises:
            NotImplementedError: Listing contacts is not implemented yet.
        """
        raise NotImplementedError(
            "ContactService.list_contacts is not implemented yet."
        )

    def search_contacts(self, query: str) -> list[Contact]:
        """Find contacts that match ``query``.

        The match is case-insensitive and covers name, address, phone
        numbers, and email.

        Args:
            query: Text to look for. Callers should pass a non-empty string.

        Returns:
            Matching contacts. An empty list means nothing matched.

        Raises:
            NotImplementedError: Contact search is not implemented yet.
        """
        raise NotImplementedError(
            "ContactService.search_contacts is not implemented yet."
        )

    def update_contact(self, name: str, contact: Contact) -> None:
        """Replace the contact currently stored under ``name``.

        Args:
            name: Name of the contact to replace. Lookup ignores case.
            contact: New contact value. Its name may differ, which renames
                the record.

        Raises:
            NotImplementedError: Contact updates are not implemented yet.
            LookupError: If no contact uses ``name``.
            ValueError: If the new name belongs to a different contact.
        """
        raise NotImplementedError(
            "ContactService.update_contact is not implemented yet."
        )

    def delete_contact(self, name: str) -> None:
        """Remove the contact named ``name``.

        Args:
            name: Name to delete. Lookup ignores case.

        Raises:
            NotImplementedError: Contact deletion is not implemented yet.
            LookupError: If no contact uses ``name``.
        """
        raise NotImplementedError(
            "ContactService.delete_contact is not implemented yet."
        )


__all__ = ["ContactService"]
