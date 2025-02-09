from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactResponse, ContactSchema
from src.services.auth import get_current_user
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 25,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieves a list of contacts for a given user.

    Args:
        skip (int): The number of contacts to skip for pagination.
        limit (int): The maximum number of contacts to return.
        db (AsyncSession): The database session.
        user (User): The user for whom the contacts are being retrieved.

    Returns:
        List[ContactResponse]: The list of contacts.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, user)
    return contacts


@router.get("/search", response_model=ContactResponse)
async def read_contact(
    contact_id: int | None = None,
    contact_first_name: str | None = None,
    contact_second_name: str | None = None,
    contact_email: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieves a contact by its ID, first name, second name or email address for a given user.

    Args:
        contact_id (int | None): The ID of the contact to retrieve.
        contact_first_name (str | None): The first name of the contact to retrieve.
        contact_second_name (str | None): The second name of the contact to retrieve.
        contact_email (str | None): The email address of the contact to retrieve.
        db (AsyncSession): The database session.
        user (User): The user for whom the contact is being retrieved.

    Returns:
        ContactResponse: The contact object if found, otherwise None.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = None
    if contact_id:
        contact = await contact_service.get_contact(contact_id, user)
    elif contact_first_name:
        contact = await contact_service.get_contact_first_name(contact_first_name, user)
    elif contact_second_name:
        contact = await contact_service.get_contact_second_name(
            contact_second_name, user
        )
    elif contact_email:
        contact = await contact_service.get_contact_email(contact_email, user)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.get("/upcoming", response_model=List[ContactResponse])
async def upcoming_birthday(
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    """
    Retrieves a list of contacts with upcoming birthday for a given user.

    Args:
        db (AsyncSession): The database session.
        user (User): The user for whom the contacts are being retrieved.

    Returns:
        List[ContactResponse]: The list of contacts with upcoming birthday.

    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_upcoming_birthday(user)
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Creates a new contact for a given user.

    Args:
        body (ContactSchema): The schema containing the contact's information.
        db (AsyncSession): The database session.
        user (User): The user for whom the contact is being created.

    Returns:
        ContactResponse: The newly created contact.

    Raises:
        HTTPException: If the contact already exists.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactSchema,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Updates a contact by its ID for a given user.

    Args:
        body (ContactSchema): The schema containing the contact's new information.
        contact_id (int): The ID of the contact to update.
        db (AsyncSession): The database session.
        user (User): The user for whom the contact is being updated.

    Returns:
        ContactResponse: The updated contact object if found, otherwise None.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Deletes a contact by its ID for a given user.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (AsyncSession): The database session.
        user (User): The user for whom the contact is being deleted.

    Returns:
        ContactResponse: The deleted contact object if found, otherwise None.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
