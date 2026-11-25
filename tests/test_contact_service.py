"""Tests for ContactService."""

from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from assistant.models.contact import Contact
from assistant.models.fields import EmailAddress, PhoneNumber
from assistant.services.contact_service import ContactService
from assistant.storage.json_storage import JSONStorage
from assistant.storage.storage import Storage
from assistant.utils import validators


class InMemoryStorage(Storage):
    """Storage double that keeps records in memory and counts saves."""

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []
        self.save_calls = 0

    def save(self, records: list[dict[str, Any]]) -> None:
        self.save_calls += 1
        self.records = [dict(record) for record in records]

    def load(self) -> list[dict[str, Any]]:
        return [dict(record) for record in self.records]


@pytest.fixture(autouse=True)
def fake_validators(monkeypatch: pytest.MonkeyPatch) -> dict[str, list[str]]:
    """Replace the validators from issue #4 with simple stand-in rules."""
    seen: dict[str, list[str]] = {"phone": [], "email": []}

    def is_valid_phone(value: str) -> bool:
        seen["phone"].append(value)
        return any(char.isdigit() for char in value) and "x" not in value

    def is_valid_email(value: str) -> bool:
        seen["email"].append(value)
        return "@" in value

    monkeypatch.setattr(validators, "is_valid_phone", is_valid_phone)
    monkeypatch.setattr(validators, "is_valid_email", is_valid_email)
    return seen


@pytest.fixture
def storage() -> InMemoryStorage:
    return InMemoryStorage()


@pytest.fixture
def service(storage: InMemoryStorage) -> ContactService:
    return ContactService(storage)


def _ada() -> Contact:
    return Contact(
        name="Ada Lovelace",
        address="London",
        phones=[PhoneNumber("+44 20 7946 0991")],
        email=EmailAddress("Ada@Example.com"),
        birthday=date(1815, 12, 10),
    )


def _alan() -> Contact:
    return Contact(
        name="Alan Turing",
        address="Manchester",
        phones=[PhoneNumber("0161 555 0100")],
        email=EmailAddress("alan@example.org"),
    )


# Creation, listing, and lookup


def test_add_contact_persists_record(
    service: ContactService, storage: InMemoryStorage
) -> None:
    contact = _ada()
    service.add_contact(contact)

    assert storage.records == [contact.to_dict()]
    assert service.list_contacts() == [contact]


def test_added_contact_is_visible_to_a_new_service(storage: InMemoryStorage) -> None:
    contact = _ada()
    ContactService(storage).add_contact(contact)

    assert ContactService(storage).get_contact(contact.id) == contact


def test_contacts_survive_json_storage_reload(tmp_path: Path) -> None:
    path = tmp_path / "contacts.json"
    contact = _ada()
    ContactService(JSONStorage(path)).add_contact(contact)

    reloaded = ContactService(JSONStorage(path))
    assert reloaded.list_contacts() == [contact]


def test_list_contacts_is_empty_without_records(service: ContactService) -> None:
    assert service.list_contacts() == []


def test_list_contacts_keeps_stored_order(service: ContactService) -> None:
    first, second = _ada(), _alan()
    service.add_contact(first)
    service.add_contact(second)

    assert [c.id for c in service.list_contacts()] == [first.id, second.id]


def test_get_contact_returns_match_or_none(service: ContactService) -> None:
    contact = _ada()
    service.add_contact(contact)

    assert service.get_contact(contact.id) == contact
    assert service.get_contact(uuid4()) is None


def test_duplicate_id_is_rejected(
    service: ContactService, storage: InMemoryStorage
) -> None:
    contact = _ada()
    service.add_contact(contact)
    duplicate = Contact(name="Someone Else", id=contact.id)

    with pytest.raises(ValueError, match="already exists"):
        service.add_contact(duplicate)
    assert storage.records == [contact.to_dict()]
    assert storage.save_calls == 1


def test_contacts_may_share_a_name(service: ContactService) -> None:
    service.add_contact(Contact(name="Ada Lovelace"))
    service.add_contact(Contact(name="Ada Lovelace"))

    assert len(service.list_contacts()) == 2


# Search


@pytest.mark.parametrize(
    "query",
    ["lovelace", "ADA LOVE", "lond", "7946", "+44 20", "example.COM", "ada@"],
)
def test_search_matches_fields_partially_and_case_insensitively(
    service: ContactService, query: str
) -> None:
    ada, alan = _ada(), _alan()
    service.add_contact(ada)
    service.add_contact(alan)

    assert service.search_contacts(query) == [ada]


def test_search_matches_phone_digits_only(service: ContactService) -> None:
    ada = _ada()
    service.add_contact(ada)
    service.add_contact(_alan())

    assert service.search_contacts("79460991") == [ada]
    assert service.search_contacts("442079") == [ada]


def test_search_returns_every_match(service: ContactService) -> None:
    ada, alan = _ada(), _alan()
    service.add_contact(ada)
    service.add_contact(alan)

    assert service.search_contacts("example") == [ada, alan]


def test_search_keeps_stored_capitalization(service: ContactService) -> None:
    service.add_contact(_ada())

    result = service.search_contacts("ADA@EXAMPLE")
    assert result[0].email is not None
    assert result[0].email.value == "Ada@Example.com"
    assert result[0].name == "Ada Lovelace"


def test_search_without_matches_returns_empty_list(service: ContactService) -> None:
    service.add_contact(_ada())

    assert service.search_contacts("nobody") == []
    assert service.search_contacts("999") == []


@pytest.mark.parametrize("query", ["", "   "])
def test_search_rejects_blank_query(service: ContactService, query: str) -> None:
    with pytest.raises(ValueError):
        service.search_contacts(query)


def test_search_rejects_non_string_query(service: ContactService) -> None:
    with pytest.raises(TypeError):
        service.search_contacts(None)  # type: ignore[arg-type]


# Update


def test_update_single_field_keeps_other_fields(
    service: ContactService,
) -> None:
    ada, alan = _ada(), _alan()
    service.add_contact(ada)
    service.add_contact(alan)

    stored = service.get_contact(ada.id)
    assert stored is not None
    service.update_contact(replace(stored, address="12 St James's Square"))

    updated = service.get_contact(ada.id)
    assert updated is not None
    assert updated.id == ada.id
    assert updated.address == "12 St James's Square"
    assert updated.name == ada.name
    assert updated.phones == ada.phones
    assert updated.email == ada.email
    assert updated.birthday == ada.birthday
    assert [c.id for c in service.list_contacts()] == [ada.id, alan.id]
    assert service.get_contact(alan.id) == alan


def test_update_can_clear_optional_fields(service: ContactService) -> None:
    ada = _ada()
    service.add_contact(ada)

    service.update_contact(replace(ada, email=None, birthday=None, phones=[]))

    updated = service.get_contact(ada.id)
    assert updated is not None
    assert updated.email is None
    assert updated.birthday is None
    assert updated.phones == []


def test_update_unknown_contact_raises_lookup_error(
    service: ContactService, storage: InMemoryStorage
) -> None:
    service.add_contact(_ada())

    with pytest.raises(LookupError):
        service.update_contact(Contact(name="Ghost"))
    assert storage.save_calls == 1


# Delete


def test_delete_contact_removes_only_that_contact(
    service: ContactService, storage: InMemoryStorage
) -> None:
    ada, alan = _ada(), _alan()
    service.add_contact(ada)
    service.add_contact(alan)

    service.delete_contact(ada.id)

    assert service.get_contact(ada.id) is None
    assert service.list_contacts() == [alan]
    assert storage.records == [alan.to_dict()]


def test_delete_unknown_contact_raises_lookup_error(
    service: ContactService, storage: InMemoryStorage
) -> None:
    service.add_contact(_ada())

    with pytest.raises(LookupError):
        service.delete_contact(uuid4())
    assert storage.save_calls == 1


# Validation


def test_add_calls_validators_with_field_values(
    service: ContactService, fake_validators: dict[str, list[str]]
) -> None:
    service.add_contact(_ada())

    assert fake_validators["phone"] == ["+44 20 7946 0991"]
    assert fake_validators["email"] == ["Ada@Example.com"]


def test_add_skips_email_validation_when_email_is_missing(
    service: ContactService, fake_validators: dict[str, list[str]]
) -> None:
    service.add_contact(Contact(name="Ada"))

    assert fake_validators["email"] == []


def test_add_rejects_invalid_phone(
    service: ContactService, storage: InMemoryStorage
) -> None:
    contact = Contact(
        name="Ada",
        phones=[PhoneNumber("+44 20"), PhoneNumber("call me x")],
    )

    with pytest.raises(ValueError, match="Invalid phone number: 'call me x'"):
        service.add_contact(contact)
    assert storage.save_calls == 0


def test_add_rejects_invalid_email(
    service: ContactService, storage: InMemoryStorage
) -> None:
    contact = Contact(name="Ada", email=EmailAddress("not-an-email"))

    with pytest.raises(ValueError, match="Invalid email address: 'not-an-email'"):
        service.add_contact(contact)
    assert storage.save_calls == 0


def test_update_rejects_invalid_values_and_keeps_stored_record(
    service: ContactService, storage: InMemoryStorage
) -> None:
    ada = _ada()
    service.add_contact(ada)

    with pytest.raises(ValueError):
        service.update_contact(replace(ada, email=EmailAddress("broken")))
    with pytest.raises(ValueError):
        service.update_contact(replace(ada, phones=[PhoneNumber("no digits")]))

    assert service.get_contact(ada.id) == ada
    assert storage.save_calls == 1
