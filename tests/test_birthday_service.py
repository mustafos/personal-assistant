"""Tests for BirthdayService."""

from datetime import date
from typing import Any

import pytest

from assistant.models.contact import Contact
from assistant.services.birthday_service import BirthdayService
from assistant.services.contact_service import ContactService
from assistant.storage.storage import Storage


class InMemoryStorage(Storage):
    """Storage double that keeps records in memory."""

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def save(self, records: list[dict[str, Any]]) -> None:
        self.records = [dict(record) for record in records]

    def load(self) -> list[dict[str, Any]]:
        return [dict(record) for record in self.records]


def _service(
    monkeypatch: pytest.MonkeyPatch, today: date, *contacts: Contact
) -> BirthdayService:
    storage = InMemoryStorage()
    storage.save([contact.to_dict() for contact in contacts])
    monkeypatch.setattr(BirthdayService, "_today", staticmethod(lambda: today))
    return BirthdayService(ContactService(storage))


def _names(contacts: list[Contact]) -> list[str]:
    return [contact.name for contact in contacts]


def test_zero_days_returns_today_only(monkeypatch: pytest.MonkeyPatch) -> None:
    service = _service(
        monkeypatch,
        date(2026, 6, 15),
        Contact(name="Today", birthday=date(1990, 6, 15)),
        Contact(name="Tomorrow", birthday=date(1990, 6, 16)),
    )

    assert _names(service.upcoming_birthdays(0)) == ["Today"]


def test_window_end_is_inclusive(monkeypatch: pytest.MonkeyPatch) -> None:
    service = _service(
        monkeypatch,
        date(2026, 6, 15),
        Contact(name="Last day", birthday=date(1990, 6, 22)),
        Contact(name="Too late", birthday=date(1990, 6, 23)),
    )

    assert _names(service.upcoming_birthdays(7)) == ["Last day"]


def test_birthday_already_passed_this_year_is_skipped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _service(
        monkeypatch,
        date(2026, 6, 15),
        Contact(name="Yesterday", birthday=date(1990, 6, 14)),
    )

    assert service.upcoming_birthdays(30) == []


def test_window_crosses_year_end(monkeypatch: pytest.MonkeyPatch) -> None:
    service = _service(
        monkeypatch,
        date(2026, 12, 28),
        Contact(name="January", birthday=date(1990, 1, 2)),
        Contact(name="New Year's Eve", birthday=date(1985, 12, 31)),
        Contact(name="Too late", birthday=date(1990, 1, 5)),
    )

    assert _names(service.upcoming_birthdays(7)) == ["New Year's Eve", "January"]


def test_contacts_without_birthday_are_skipped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _service(
        monkeypatch,
        date(2026, 6, 15),
        Contact(name="Unknown"),
        Contact(name="Known", birthday=date(1990, 6, 15)),
    )

    assert _names(service.upcoming_birthdays(7)) == ["Known"]


def test_no_matches_returns_empty_list(monkeypatch: pytest.MonkeyPatch) -> None:
    empty = _service(monkeypatch, date(2026, 6, 15))
    assert empty.upcoming_birthdays(7) == []

    far = _service(
        monkeypatch,
        date(2026, 6, 15),
        Contact(name="Far", birthday=date(1990, 9, 1)),
    )
    assert far.upcoming_birthdays(7) == []


def test_results_are_sorted_by_next_birthday(monkeypatch: pytest.MonkeyPatch) -> None:
    service = _service(
        monkeypatch,
        date(2026, 6, 15),
        Contact(name="Third", birthday=date(2000, 6, 20)),
        Contact(name="First", birthday=date(1970, 6, 16)),
        Contact(name="Second", birthday=date(1980, 6, 18)),
    )

    assert _names(service.upcoming_birthdays(10)) == ["First", "Second", "Third"]


def test_result_keeps_contact_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    contact = Contact(name="Ada", birthday=date(1815, 6, 16))
    service = _service(monkeypatch, date(2026, 6, 15), contact)

    assert service.upcoming_birthdays(1) == [contact]


def test_feb_29_counts_as_feb_28_in_non_leap_year(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    leapling = Contact(name="Leapling", birthday=date(2000, 2, 29))

    on_28th = _service(monkeypatch, date(2027, 2, 28), leapling)
    assert _names(on_28th.upcoming_birthdays(0)) == ["Leapling"]

    after = _service(monkeypatch, date(2027, 3, 1), leapling)
    assert after.upcoming_birthdays(0) == []


def test_feb_29_is_used_in_leap_year(monkeypatch: pytest.MonkeyPatch) -> None:
    leapling = Contact(name="Leapling", birthday=date(2000, 2, 29))

    on_28th = _service(monkeypatch, date(2028, 2, 28), leapling)
    assert on_28th.upcoming_birthdays(0) == []
    assert _names(on_28th.upcoming_birthdays(1)) == ["Leapling"]


def test_feb_29_across_year_end_into_non_leap_year(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    leapling = Contact(name="Leapling", birthday=date(2000, 2, 29))
    service = _service(monkeypatch, date(2026, 12, 31), leapling)

    # 2026-12-31 + 59 days is 2027-02-28.
    assert _names(service.upcoming_birthdays(59)) == ["Leapling"]
    assert service.upcoming_birthdays(58) == []


def test_negative_days_raise_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    service = _service(monkeypatch, date(2026, 6, 15))

    with pytest.raises(ValueError):
        service.upcoming_birthdays(-1)


@pytest.mark.parametrize("value", [1.5, True, "7", None])
def test_non_integer_days_raise_type_error(
    monkeypatch: pytest.MonkeyPatch, value: object
) -> None:
    service = _service(monkeypatch, date(2026, 6, 15))

    with pytest.raises(TypeError):
        service.upcoming_birthdays(value)  # type: ignore[arg-type]
