from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.database.models import Contact, User
from src.schemas import ContactSchema


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User):
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def get_contact_by_first_name(self, contact_name: str, user: User) -> Contact | None:
        stmt = select(Contact).filter_by(first_name=contact_name, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def get_contact_by_second_name(self, contact_name: str, user: User) -> Contact | None:
        stmt = select(Contact).filter_by(second_name=contact_name, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def get_contact_by_email(self, contact_email: str, user: User) -> Contact | None:
        stmt = select(Contact).filter_by(email=contact_email, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def get_upcoming_birthday(self, user: User):
        today = date.today()
        end_date = today + timedelta(days=7)
        stmt = select(Contact).filter_by(user=user).where(
            func.to_char(Contact.birthday, "MM-DD").between(
                today.strftime("%m-%d"), end_date.strftime("%m-%d")
            )
        )
        contact = await self.db.execute(stmt)
        return contact.scalars().all()

    async def create_contact(self, body: ContactSchema, user: User):
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return await self.get_contact_by_id(contact.id, user)

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
            self, contact_id: int, body: ContactSchema, user: User
    ) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact
