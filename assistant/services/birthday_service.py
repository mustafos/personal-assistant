"""Birthday queries over stored contacts."""

import calendar
from datetime import date, timedelta

from assistant.models.contact import Contact
from assistant.services.contact_service import ContactService


class BirthdayService:
    """Find contacts with upcoming birthdays.

    Read contacts through :meth:`ContactService.list_contacts` and keep each
    contact's ``id``. This service does not receive a storage backend.
    """

    def __init__(self, contact_service: ContactService) -> None:
        """Store the contact service used to read birthdays.

        Args:
            contact_service: Service that will provide stored contacts.
        """
        self._contact_service = contact_service

    @staticmethod
    def _anniversary_for_year(birthday: date, year: int) -> date:
        """Return the birthday date in ``year`` (Feb 29 -> Feb 28 in non-leap years)."""
        if birthday.month == 2 and birthday.day == 29 and not calendar.isleap(year):
            return date(year, 2, 28)
        return date(year, birthday.month, birthday.day)

    def _next_occurrence(self, birthday: date, reference_date: date) -> date:
        """Return the next birthday date on or after ``reference_date``."""
        anniversary = self._anniversary_for_year(birthday, reference_date.year)
        if anniversary < reference_date:
            anniversary = self._anniversary_for_year(birthday, reference_date.year + 1)
        return anniversary

    def upcoming_birthdays(self, within_days: int) -> list[Contact]:
        """Return contacts whose birthday falls inside the given window.

        The window starts today and includes the day ``within_days`` days
        from today. Contacts without a birthday are skipped. In non-leap years,
        Feb 29 is treated as Feb 28.

        Args:
            within_days: Length of the window. Zero means today only.

        Returns:
            Matching contacts.

        Raises:
            TypeError: If ``within_days`` is not an integer.
            ValueError: If ``within_days`` is negative.
        """
        if not isinstance(within_days, int) or isinstance(within_days, bool):
            raise TypeError("within_days must be an integer.")
        if within_days < 0:
            raise ValueError("within_days must be zero or greater.")

        today = date.today()
        window_end = today + timedelta(days=within_days)

        upcoming: list[Contact] = []
        for contact in self._contact_service.list_contacts():
            if contact.birthday is None:
                continue

            next_birthday = self._next_occurrence(contact.birthday, today)
            if today <= next_birthday <= window_end:
                upcoming.append(contact)

        return upcoming


__all__ = ["BirthdayService"]
