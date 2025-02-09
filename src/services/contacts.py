from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.contacts import ContactRepository
from src.schemas import ContactSchema


def _handle_integrity_error(e: IntegrityError):
    """
    Handles integrity errors by either raising 400 or 409 HTTP exceptions
    depending on the error message.
    """
    print(f"Error: {e.orig}")
    if "duplicate key value" in str(e.orig):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Тег з такою назвою вже існує.",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Помилка цілісності даних.",
        )


class ContactService:
    """
    Service class for managing contacts.

    This class acts as an intermediary between the API layer and the repository,
    handling business logic and error handling.
    """

    def __init__(self, db: AsyncSession):
        self.contact_repo = ContactRepository(db)

    async def create_contact(self, body: ContactSchema, user: User):
        """
        Creates a new contact for a given user.

        Args:
            body (ContactSchema): The contact data to be created.
            user (User): The user for whom the contact is being created.

        Returns:
            Contact: The newly created contact.

        Raises:
            HTTPException: If the contact already exists.
        """
        try:
            return await self.contact_repo.create_contact(body, user)
        except IntegrityError as e:
            await self.contact_repo.db.rollback()
            _handle_integrity_error(e)

    async def get_contacts(self, skip: int, limit: int, user: User):
        """
        Retrieves a list of contacts for a given user.

        Args:
            skip (int): The number of contacts to skip for pagination.
            limit (int): The maximum number of contacts to return.
            user (User): The user for whom the contacts are being retrieved.

        Returns:
            list[Contact]: The list of contacts.

        """
        return await self.contact_repo.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        """
        Retrieves a contact by its ID for a given user.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user for whom the contact is being retrieved.

        Returns:
            Contact | None: The contact object if found, otherwise None.

        """
        return await self.contact_repo.get_contact_by_id(contact_id, user)

    async def get_contact_first_name(self, contact_name: str, user: User):
        """
        Retrieves a contact by its first name for a given user.

        Args:
            contact_name (str): The first name of the contact to retrieve.
            user (User): The user for whom the contact is being retrieved.

        Returns:
            Contact | None: The contact object if found, otherwise None.
        """
        return await self.contact_repo.get_contact_by_first_name(contact_name, user)

    async def get_contact_second_name(self, contact_name: str, user: User):
        """
        Retrieves a contact by its second name for a given user.

        Args:
            contact_name (str): The second name of the contact to retrieve.
            user (User): The user for whom the contact is being retrieved.

        Returns:
            Contact | None: The contact object if found, otherwise None.
        """
        return await self.contact_repo.get_contact_by_second_name(contact_name, user)

    async def get_contact_email(self, contact_email: str, user: User):
        """
        Retrieves a contact by its email address for a given user.

        Args:
            contact_email (str): The email address of the contact to retrieve.
            user (User): The user for whom the contact is being retrieved.

        Returns:
            Contact | None: The contact object if found, otherwise None.
        """
        return await self.contact_repo.get_contact_by_email(contact_email, user)

    async def get_upcoming_birthday(self, user: User):
        """
        Retrieves the contacts with upcoming birthday for a given user.

        Args:
            user (User): The user for whom the contacts are being retrieved.

        Returns:
            list[Contact]: The list of contacts with upcoming birthday.
        """
        return await self.contact_repo.get_upcoming_birthday(user)

    async def update_contact(self, contact_id: int, body: ContactSchema, user: User):
        """
        Updates a contact by its ID for a given user.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactSchema): The schema containing the contact's new information.
            user (User): The user for whom the contact is being updated.

        Returns:
            Contact: The updated contact object if found, otherwise None.

        Raises:
            HTTPException: If the contact already exists.
        """
        try:
            return await self.contact_repo.update_contact(contact_id, body, user)
        except IntegrityError as e:
            await self.contact_repo.db.rollback()
            _handle_integrity_error(e)

    async def remove_contact(self, contact_id: int, user: User):
        """
        Delete a contact by its ID for a given user.

        Args:
            contact_id (int): The ID of the contact to delete.
            user (User): The user for whom the contact is being deleted.

        Returns:
            Contact | None: The deleted contact object if found, otherwise None.
        """
        return await self.contact_repo.remove_contact(contact_id, user)
