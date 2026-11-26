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
    """

    def __init__(self, storage: Storage) -> None:
        """Store the persistence dependency.

        Args:
            storage: Backend for the contact collection.
        """
        self._storage = storage

    def _load_contacts(self) -> list[Contact]:
        """Load stored contact records and rebuild Contact instances."""
        raw_records = self._storage.load()
        return [Contact.from_dict(record) for record in raw_records]

    def _save_contacts(self, contacts: list[Contact]) -> None:
        """Serialize Contact instances and persist them via storage."""
        self._storage.save([contact.to_dict() for contact in contacts])

    @staticmethod
    def _matches_query(contact: Contact, needle: str) -> bool:
        """Check whether any contact field contains the lowercased needle."""
        parts: list[str] = []

        if contact.name:
            parts.append(str(contact.name))
        if contact.address:
            parts.append(str(contact.address))
        if contact.email:
            parts.append(str(contact.email))
        for phone in contact.phones:
            parts.append(str(phone))

        return any(needle in part.casefold() for part in parts)

    def add_contact(self, contact: Contact) -> None:
        """Store a new contact.

        Args:
            contact: Contact to add.

        Raises:
            ValueError: If a contact with the same id already exists.
        """
        contacts = self._load_contacts()
        if any(existing.id == contact.id for existing in contacts):
            raise ValueError(f"Contact with id {contact.id} already exists.")

        contacts.append(contact)
        self._save_contacts(contacts)

    def get_contact(self, contact_id: UUID) -> Contact | None:
        """Return the contact identified by ``contact_id``.

        Args:
            contact_id: Identifier stored on the contact.

        Returns:
            The stored contact, or None when the id is unknown.
        """
        for contact in self._load_contacts():
            if contact.id == contact_id:
                return contact
        return None

    def list_contacts(self) -> list[Contact]:
        """Return every stored contact.

        Returns:
            All contacts. The order matches the stored collection.
        """
        return self._load_contacts()

    def search_contacts(self, query: str) -> list[Contact]:
        """Find contacts that match ``query``.

        The match is case-insensitive and covers name, address, phone
        numbers, and email.

        Args:
            query: Text to look for. Callers should pass a non-empty string.

        Returns:
            Matching contacts. An empty list means nothing matched.
        """
        needle = query.strip().casefold()
        if not needle:
            return []

        return [
            contact
            for contact in self._load_contacts()
            if self._matches_query(contact, needle)
        ]

    def update_contact(self, contact: Contact) -> None:
        """Replace the stored contact that has ``contact.id``.

        Args:
            contact: New contact value, including the id of the contact to
                replace. The name may change and may match another contact.

        Raises:
            LookupError: If no stored contact uses ``contact.id``.
        """
        contacts = self._load_contacts()
        for index, existing in enumerate(contacts):
            if existing.id == contact.id:
                contacts[index] = contact
                self._save_contacts(contacts)
                return

        raise LookupError(f"Contact not found: {contact.id}")

    def delete_contact(self, contact_id: UUID) -> None:
        """Remove the contact identified by ``contact_id``.

        Args:
            contact_id: Identifier of the contact to remove.

        Raises:
            LookupError: If no stored contact uses ``contact_id``.
        """
        contacts = self._load_contacts()
        remaining = [existing for existing in contacts if existing.id != contact_id]
        if len(remaining) == len(contacts):
            raise LookupError(f"Contact not found: {contact_id}")

        self._save_contacts(remaining)


__all__ = ["ContactService"]
