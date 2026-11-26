"""Birthday queries over stored contacts."""

from assistant.models.contact import Contact
from assistant.services.contact_service import ContactService


class BirthdayService:
    """Find contacts with upcoming birthdays.

    Read contacts through :meth:`ContactService.list_contacts` and keep each
    contact's ``id``. This service does not receive a storage backend and does
    not calculate birthdays yet.
    """

    def __init__(self, contact_service: ContactService) -> None:
        """Store the contact service used to read birthdays.

        Args:
            contact_service: Service that will provide stored contacts.
        """
        self._contact_service = contact_service

    def upcoming_birthdays(self, within_days: int) -> list[Contact]:
        """Return contacts whose birthday falls inside the given window.

        The window starts today and includes the day ``within_days`` days
        from today. Contacts without a birthday are skipped. Feb 29 is still
        to be defined by the implementation.

        Args:
            within_days: Length of the window. Zero means today only.

        Returns:
            Matching contacts. Order is not significant yet.

        Raises:
            NotImplementedError: The date calculation is not implemented yet.
            TypeError: If ``within_days`` is not an integer.
            ValueError: If ``within_days`` is negative.
        """
        if not isinstance(within_days, int) or isinstance(within_days, bool):
            raise TypeError("within_days must be an integer.")
        if within_days < 0:
            raise ValueError("within_days must be zero or greater.")
        raise NotImplementedError(
            "BirthdayService.upcoming_birthdays is not implemented yet."
        )


__all__ = ["BirthdayService"]
