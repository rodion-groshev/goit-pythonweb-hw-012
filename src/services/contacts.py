from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.contacts import ContactRepository
from src.schemas import ContactSchema


def _handle_integrity_error(e: IntegrityError):
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
    def __init__(self, db: AsyncSession):
        self.contact_repo = ContactRepository(db)

    async def create_contact(self, body: ContactSchema, user: User):
        try:
            return await self.contact_repo.create_contact(body, user)
        except IntegrityError as e:
            await self.contact_repo.db.rollback()
            _handle_integrity_error(e)

    async def get_contacts(self, skip: int, limit: int, user: User):
        return await self.contact_repo.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        return await self.contact_repo.get_contact_by_id(contact_id, user)

    async def get_contact_first_name(self, contact_name: str, user: User):
        return await self.contact_repo.get_contact_by_first_name(contact_name, user)

    async def get_contact_second_name(self, contact_name: str, user: User):
        return await self.contact_repo.get_contact_by_second_name(contact_name, user)

    async def get_contact_email(self, contact_email: str, user: User):
        return await self.contact_repo.get_contact_by_email(contact_email, user)

    async def get_upcoming_birthday(self, user: User):
        return await self.contact_repo.get_upcoming_birthday(user)

    async def update_contact(self, contact_id: int, body: ContactSchema, user: User):
        try:
            return await self.contact_repo.update_contact(contact_id, body, user)
        except IntegrityError as e:
            await self.contact_repo.db.rollback()
            _handle_integrity_error(e)

    async def remove_contact(self, contact_id: int, user: User):
        return await self.contact_repo.remove_contact(contact_id, user)
