"""Business operations for contacts."""

from uuid import UUID

import assistant.utils.validators as validators
from assistant.models.contact import Contact
from assistant.storage.storage import Storage


class ContactService:
    """Create, read, search, update, and delete contacts.

    Pass a :class:`~assistant.storage.storage.Storage` instance. This class
    does not open files or import the JSON backend. Records are loaded with
    ``storage.load()``, rebuilt with :meth:`Contact.from_dict`, and saved as
    ``contact.to_dict()`` mappings with ``storage.save``. A stored record is
    matched by ``Contact.id``. Names are not unique, so they cannot identify
    a record. If the stored collection holds the same id more than once,
    operations act on the first match.

    Phone numbers and email addresses are checked with
    :func:`assistant.utils.validators.is_valid_phone` and
    :func:`assistant.utils.validators.is_valid_email` before a contact is
    saved. Search compares text case-insensitively. Stored capitalization is
    kept.
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
            ValueError: If a contact with the same id already exists, or a
                phone number or email address fails validation.
        """
        _validate(contact)
        contacts = self._load()
        if _index_of(contacts, contact.id) is not None:
            raise ValueError(f"Contact with id {contact.id} already exists.")
        contacts.append(contact)
        self._save(contacts)

    def get_contact(self, contact_id: UUID) -> Contact | None:
        """Return the contact identified by ``contact_id``.

        Args:
            contact_id: Identifier stored on the contact.

        Returns:
            The stored contact, or None when the id is unknown.
        """
        contacts = self._load()
        index = _index_of(contacts, contact_id)
        return None if index is None else contacts[index]

    def list_contacts(self) -> list[Contact]:
        """Return every stored contact.

        Returns:
            All contacts. The order matches the stored collection.
        """
        return self._load()

    def search_contacts(self, query: str) -> list[Contact]:
        """Find contacts that match ``query``.

        The match is a case-insensitive substring search over name, address,
        phone numbers, and email. When the query contains digits, phone
        numbers also match on digits alone, so ``79460991`` finds
        ``+44 20 7946 0991``.

        Args:
            query: Text to look for.

        Returns:
            Matching contacts in stored order. An empty list means nothing
            matched.

        Raises:
            TypeError: If ``query`` is not a string.
            ValueError: If ``query`` is blank.
        """
        if not isinstance(query, str):
            raise TypeError("Search query must be a string.")
        needle = " ".join(query.split()).casefold()
        if not needle:
            raise ValueError("Search query must not be empty.")
        digits = _digits(needle)
        return [
            contact for contact in self._load() if _matches(contact, needle, digits)
        ]

    def update_contact(self, contact: Contact) -> None:
        """Replace the stored contact that has ``contact.id``.

        To change one field, pass a copy of the stored contact made with
        :func:`dataclasses.replace`. Fields that are not replaced keep their
        values, and the contact keeps its position in the collection.

        Args:
            contact: New contact value, including the id of the contact to
                replace. The name may change and may match another contact.

        Raises:
            LookupError: If no stored contact uses ``contact.id``.
            ValueError: If a phone number or email address fails validation.
        """
        _validate(contact)
        contacts = self._load()
        index = _index_of(contacts, contact.id)
        if index is None:
            raise LookupError(f"Contact with id {contact.id} not found.")
        contacts[index] = contact
        self._save(contacts)

    def delete_contact(self, contact_id: UUID) -> None:
        """Remove the contact identified by ``contact_id``.

        Args:
            contact_id: Identifier of the contact to remove.

        Raises:
            LookupError: If no stored contact uses ``contact_id``.
        """
        contacts = self._load()
        index = _index_of(contacts, contact_id)
        if index is None:
            raise LookupError(f"Contact with id {contact_id} not found.")
        del contacts[index]
        self._save(contacts)

    def _load(self) -> list[Contact]:
        return [Contact.from_dict(record) for record in self._storage.load()]

    def _save(self, contacts: list[Contact]) -> None:
        self._storage.save([contact.to_dict() for contact in contacts])


def _index_of(contacts: list[Contact], contact_id: UUID) -> int | None:
    for index, contact in enumerate(contacts):
        if contact.id == contact_id:
            return index
    return None


def _validate(contact: Contact) -> None:
    for phone in contact.phones:
        if not validators.is_valid_phone(phone.value):
            raise ValueError(f"Invalid phone number: {phone.value!r}.")
    if contact.email is not None and not validators.is_valid_email(contact.email.value):
        raise ValueError(f"Invalid email address: {contact.email.value!r}.")


def _digits(text: str) -> str:
    return "".join(char for char in text if char.isdigit())


def _matches(contact: Contact, needle: str, digits: str) -> bool:
    fields = [contact.name, contact.address]
    fields.extend(phone.value for phone in contact.phones)
    if contact.email is not None:
        fields.append(contact.email.value)
    if any(needle in field.casefold() for field in fields):
        return True
    return bool(digits) and any(
        digits in _digits(phone.value) for phone in contact.phones
    )


__all__ = ["ContactService"]
