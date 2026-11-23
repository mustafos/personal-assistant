"""Business operations for contacts."""

from uuid import UUID

from assistant.models.contact import Contact
from assistant.storage.storage import Storage


class ContactService:
    """Create, read, search, update, and delete contacts.

    Pass a :class:`~assistant.storage.storage.Storage` instance. This class
    must not open files or import the JSON backend. An implementation should
    load records with ``storage.load()``, rebuild them with
    :meth:`Contact.from_dict`, and save ``contact.to_dict()`` mappings with
    ``storage.save``. Match a stored record by ``Contact.id``. Names are not
    unique, so they cannot identify a record.

    Search may compare text case-insensitively. Stored capitalization is kept.
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
            ValueError: If a contact with the same id already exists.
        """
        raise NotImplementedError("ContactService.add_contact is not implemented yet.")

    def get_contact(self, contact_id: UUID) -> Contact | None:
        """Return the contact identified by ``contact_id``.

        Args:
            contact_id: Identifier stored on the contact.

        Returns:
            The stored contact, or None when the id is unknown.

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

    def update_contact(self, contact: Contact) -> None:
        """Replace the stored contact that has ``contact.id``.

        Args:
            contact: New contact value, including the id of the contact to
                replace. The name may change and may match another contact.

        Raises:
            NotImplementedError: Contact updates are not implemented yet.
            LookupError: If no stored contact uses ``contact.id``.
        """
        raise NotImplementedError(
            "ContactService.update_contact is not implemented yet."
        )

    def delete_contact(self, contact_id: UUID) -> None:
        """Remove the contact identified by ``contact_id``.

        Args:
            contact_id: Identifier of the contact to remove.

        Raises:
            NotImplementedError: Contact deletion is not implemented yet.
            LookupError: If no stored contact uses ``contact_id``.
        """
        raise NotImplementedError(
            "ContactService.delete_contact is not implemented yet."
        )


__all__ = ["ContactService"]
