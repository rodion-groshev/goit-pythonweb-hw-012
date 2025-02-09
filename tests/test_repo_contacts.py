from datetime import date, timedelta

from unittest.mock import AsyncMock, MagicMock

import pytest
from conftest import test_user
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactSchema


test_contacts = [
    {
        "first_name": "First",
        "second_name": "Last",
        "email": "user@gmail.com",
        "phone": "0671234567",
        "birthday": str(date(2000, 1, 1)),
        "additional": "text",
    },
    {
        "first_name": "First2",
        "second_name": "Last2",
        "email": "user2@gmail.com",
        "phone": "0677654321",
        "birthday": str(date(2000, 11, 11)),
        "additional": "text2",
    },
]


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username=test_user["username"], email=test_user["email"])


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()

    contacts_to_get = [
        Contact(
            id=i + 1,
            first_name=contact["first_name"],
            second_name=contact["second_name"],
            email=contact["email"],
            phone=contact["phone"],
            birthday=contact["birthday"],
            additional=contact["additional"],
            user=user,
        )
        for i, contact in enumerate(test_contacts[:2])
    ]

    mock_result.scalars.return_value.all.return_value = contacts_to_get
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_contacts(skip=0, limit=10, user=user)

    assert len(contacts) == 2
    assert contacts[0].first_name == test_contacts[0]["first_name"]
    assert contacts[0].second_name == test_contacts[0]["second_name"]
    assert contacts[0].email == test_contacts[0]["email"]
    assert contacts[0].phone == test_contacts[0]["phone"]
    assert contacts[0].birthday == test_contacts[0]["birthday"]
    assert contacts[0].additional == test_contacts[0]["additional"]
    assert contacts == contacts_to_get


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    contacts_to_get = [
        Contact(
            id=i + 1,
            first_name=contact["first_name"],
            second_name=contact["second_name"],
            email=contact["email"],
            phone=contact["phone"],
            birthday=contact["birthday"],
            additional=contact["additional"],
            user=user,
        )
        for i, contact in enumerate(test_contacts[:2])
    ]
    mock_result.scalar_one_or_none.return_value = contacts_to_get[0]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contact = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    assert contact is not None
    assert contact.id == 1
    assert contact.first_name == test_contacts[0]["first_name"]


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    # Setup
    contact_old = Contact(
        id=1,
        first_name=test_contacts[0]["first_name"],
        second_name=test_contacts[0]["second_name"],
        email=test_contacts[0]["email"],
        phone=test_contacts[0]["phone"],
        birthday=test_contacts[0]["birthday"],
        additional=test_contacts[0]["additional"],
    )
    contact_new = ContactSchema(
        first_name="updated first name",
        second_name="updated second name",
        email="updated@email.com",
        phone="1234567890",
        birthday=str(date(2020, 1, 1)),
        additional="updated additional data",
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact_old
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.update_contact(
        contact_id=1, body=contact_new, user=user
    )

    assert result is not None
    assert result.first_name == contact_new.first_name
    assert result.second_name == contact_new.second_name
    assert result.email == contact_new.email
    assert result.phone == contact_new.phone
    assert result.birthday == contact_new.birthday
    assert result.additional == contact_new.additional
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(contact_old)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
    # Setup
    existing_contact = Contact(
        id=1,
        first_name=test_contacts[0]["first_name"],
        second_name=test_contacts[0]["second_name"],
        email=test_contacts[0]["email"],
        phone=test_contacts[0]["phone"],
        birthday=test_contacts[0]["birthday"],
        additional=test_contacts[0]["additional"],
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.remove_contact(contact_id=1, user=user)

    assert result is not None
    assert result.first_name == existing_contact.first_name
    assert result.second_name == existing_contact.second_name
    assert result.email == existing_contact.email
    assert result.phone == existing_contact.phone
    assert result.birthday == existing_contact.birthday
    assert result.additional == existing_contact.additional
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()
