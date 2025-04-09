from cryptography.fernet import Fernet
import os

from dotenv import load_dotenv
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import PasswordEntry
from backend.schemas import PasswordEntryCreate

load_dotenv()

class PasswordRepository:
    _fernet = Fernet("W9Er9gRuwAQRM4AtdBX5cQ_5Z-3XZ3bwM5SZ3yH0z2Q=")

    @classmethod
    def _encrypt_password(cls, password: str) -> bytes:
        return cls._fernet.encrypt(password.encode())

    @classmethod
    def _decrypt_password(cls, encrypted_password: bytes) -> str:
        return cls._fernet.decrypt(encrypted_password).decode()

    @staticmethod
    async def create_password_entry(
        session: AsyncSession,
        id_user: int,
        entry_data: PasswordEntryCreate,
    ):
        encrypted_password = PasswordRepository._encrypt_password(entry_data.password)
        new_entry = PasswordEntry(
            id_user=id_user,
            website=entry_data.website,
            username=entry_data.username,
            encrypted_password=encrypted_password,
            notes=entry_data.notes,
        )
        session.add(new_entry)
        await session.commit()
        await session.refresh(new_entry)
        return new_entry

    @staticmethod
    async def get_user_entries(session: AsyncSession, id_user: int):
        result = await session.execute(
            select(PasswordEntry)
            .where(PasswordEntry.id_user == id_user)
            .order_by(PasswordEntry.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_entry_by_id(session: AsyncSession, id_entry: int, id_user: int):
        result = await session.execute(
            select(PasswordEntry)
            .where(PasswordEntry.id_entry == id_entry)
            .where(PasswordEntry.id_user == id_user)
        )
        return result.scalars().first()

    @staticmethod
    async def decrypt_entry_password(entry: PasswordEntry) -> str:
        return PasswordRepository._decrypt_password(entry.encrypted_password)

    @staticmethod
    async def update_password_entry(
            session: AsyncSession,
            entry_id: int,
            user_id: int,
            update_data: dict
    ):
        if 'password' in update_data:
            update_data['encrypted_password'] = PasswordRepository._encrypt_password(update_data.pop('password'))

        stmt = (
            update(PasswordEntry)
            .where(
                (PasswordEntry.id_entry == entry_id) &
                (PasswordEntry.id_user == user_id)
            )
            .values(**update_data)
            .returning(PasswordEntry)
        )

        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one()

    @staticmethod
    async def delete_password_entry(
            session: AsyncSession,
            entry_id: int,
            user_id: int
    ):
        stmt = (
            delete(PasswordEntry)
            .where(
                (PasswordEntry.id_entry == entry_id) &
                (PasswordEntry.id_user == user_id)
            )
        )
        await session.execute(stmt)
        await session.commit()