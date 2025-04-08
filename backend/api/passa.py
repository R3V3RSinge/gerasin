from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_session
from backend.repositories import PasswordRepository
from backend.schemas import (
    PasswordEntryCreate,
    PasswordEntryResponse,
    PasswordEntryWithPasswordResponse,
)
from backend.dependices import get_current_user
from backend.models import User

router = APIRouter(prefix="/passwords", tags=["passwords"])


@router.post("/", response_model=PasswordEntryResponse)
async def create_password_entry(
        entry_data: PasswordEntryCreate,
        session: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user),
):
    entry = await PasswordRepository.create_password_entry(
        session, user.id_user, entry_data
    )
    return entry


@router.get("/", response_model=list[PasswordEntryResponse])
async def get_password_entries(
        session: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user),
):
    entries = await PasswordRepository.get_user_entries(session, user.id_user)
    return entries


@router.get("/{entry_id}/", response_model=PasswordEntryWithPasswordResponse)
async def get_password_entry(
        entry_id: int,
        session: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user),
):
    entry = await PasswordRepository.get_entry_by_id(session, entry_id, user.id_user)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    decrypted_password = await PasswordRepository.decrypt_entry_password(entry)
    return {
        **PasswordEntryResponse.from_orm(entry).dict(),
        "password": decrypted_password,
    }

# Можно добавить эндпоинты для обновления и удаления записей