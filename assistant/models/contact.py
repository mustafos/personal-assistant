"""Contact entity."""

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from assistant.models.fields import EmailAddress, PhoneNumber, normalize_label


@dataclass(slots=True)
class Contact:
    """A person stored in the address book.

    ``name`` identifies a contact. Persistence code should convert instances
    with :meth:`to_dict` and restore them with :meth:`from_dict`.
    """

    name: str
    address: str = ""
    phones: list[PhoneNumber] = field(default_factory=list)
    email: EmailAddress | None = None
    birthday: date | None = None

    def __post_init__(self) -> None:
        self.name = normalize_label(self.name, field_name="Contact name")
        self.address = normalize_label(
            self.address,
            field_name="Contact address",
            allow_empty=True,
        )
        self.phones = list(self.phones)
        for phone in self.phones:
            if not isinstance(phone, PhoneNumber):
                raise TypeError("Each phone must be a PhoneNumber.")
        if self.email is not None and not isinstance(self.email, EmailAddress):
            raise TypeError("Email must be an EmailAddress or None.")
        if self.birthday is not None and not isinstance(self.birthday, date):
            raise TypeError("Birthday must be a datetime.date or None.")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready mapping.

        Phones and email are plain strings. ``birthday`` is an ISO date
        (``YYYY-MM-DD``) or ``None``.
        """
        return {
            "name": self.name,
            "address": self.address,
            "phones": [phone.value for phone in self.phones],
            "email": None if self.email is None else self.email.value,
            "birthday": None if self.birthday is None else self.birthday.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Contact":
        """Rebuild a contact from :meth:`to_dict` output.

        Args:
            data: Mapping with ``name`` and optional contact fields.

        Returns:
            A new contact.

        Raises:
            TypeError: If ``data`` or a field has an unexpected type.
            KeyError: If ``name`` is missing.
            ValueError: If a field value cannot be used.
        """
        if not isinstance(data, dict):
            raise TypeError("Contact data must be a mapping.")

        phones_raw = data.get("phones", [])
        if not isinstance(phones_raw, list):
            raise TypeError("Contact field 'phones' must be a list.")
        phones = [PhoneNumber(item) for item in phones_raw]

        email_raw = data.get("email")
        if email_raw is None:
            email = None
        elif isinstance(email_raw, str):
            email = EmailAddress(email_raw)
        else:
            raise TypeError("Contact field 'email' must be a string or null.")

        birthday_raw = data.get("birthday")
        if birthday_raw is None:
            birthday = None
        elif isinstance(birthday_raw, str):
            birthday = date.fromisoformat(birthday_raw)
        else:
            raise TypeError("Contact field 'birthday' must be a string or null.")

        address = data.get("address", "")
        if not isinstance(address, str):
            raise TypeError("Contact field 'address' must be a string.")

        name = data["name"]
        if not isinstance(name, str):
            raise TypeError("Contact field 'name' must be a string.")

        return cls(
            name=name,
            address=address,
            phones=phones,
            email=email,
            birthday=birthday,
        )


__all__ = ["Contact"]
