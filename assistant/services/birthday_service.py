"""Birthday queries over stored contacts."""

import calendar
from datetime import date, timedelta

from assistant.models.contact import Contact
from assistant.services.contact_service import ContactService


class BirthdayService:
    """Find contacts with upcoming birthdays.

    Contacts are read through :meth:`ContactService.list_contacts`. This
    service does not receive a storage backend.

    A birthday on 29 February is celebrated on 28 February in years that are
    not leap years.
    """

    def __init__(self, contact_service: ContactService) -> None:
        """Store the contact service used to read birthdays.

        Args:
            contact_service: Service that provides stored contacts.
        """
        self._contact_service = contact_service

    def upcoming_birthdays(self, within_days: int) -> list[Contact]:
        """Return contacts whose birthday falls inside the given window.

        The window starts today and includes the day ``within_days`` days
        from today. It may cross the end of the year. Contacts without a
        birthday are skipped. A 29 February birthday counts as 28 February
        in a non-leap year.

        Args:
            within_days: Length of the window. Zero means today only.

        Returns:
            Matching contacts, nearest birthday first. Contacts with the same
            date keep their stored order. An empty list means none matched.

        Raises:
            TypeError: If ``within_days`` is not an integer.
            ValueError: If ``within_days`` is negative.
        """
        if not isinstance(within_days, int) or isinstance(within_days, bool):
            raise TypeError("within_days must be an integer.")
        if within_days < 0:
            raise ValueError("within_days must be zero or greater.")

        today = self._today()
        end = today + timedelta(days=within_days)
        upcoming: list[tuple[date, Contact]] = []
        for contact in self._contact_service.list_contacts():
            if contact.birthday is None:
                continue
            next_date = _next_birthday(contact.birthday, today)
            if next_date <= end:
                upcoming.append((next_date, contact))
        upcoming.sort(key=lambda item: item[0])
        return [contact for _, contact in upcoming]

    @staticmethod
    def _today() -> date:
        return date.today()


def _birthday_in_year(birthday: date, year: int) -> date:
    if birthday.month == 2 and birthday.day == 29 and not calendar.isleap(year):
        return date(year, 2, 28)
    return birthday.replace(year=year)


def _next_birthday(birthday: date, today: date) -> date:
    candidate = _birthday_in_year(birthday, today.year)
    if candidate < today:
        candidate = _birthday_in_year(birthday, today.year + 1)
    return candidate


__all__ = ["BirthdayService"]
