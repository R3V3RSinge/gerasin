# backend/api/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from backend.models import User
from backend.repositories import UserRepository, RevokedTokenRepository
from backend.db import get_session
from backend.schemas import UserCreate, UserLogin, Token, UserResponse, UserProfile
from backend.security import (
    hash_password,
    verify_password,
    create_access_token,
    oauth2_scheme,
    decode_token,
)
from backend.dependices import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/", response_model=UserResponse)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    user = await UserRepository.get_user_by_email(session, user_data.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = await UserRepository.create_user(
        session, user_data.email, user_data.password
    )
    return new_user


@router.post("/login/", response_model=Token)
async def login(user_data: UserLogin, session: AsyncSession = Depends(get_session)):
    user = await UserRepository.get_user_by_email(session, user_data.email)
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/users/", response_model=list[UserResponse])
async def get_users(
    session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await UserRepository.get_all_users(session)


@router.get("/profile/", response_model=UserProfile)
async def get_profile(user: User = Depends(get_current_user)):
    return UserProfile(email=user.email, is_admin=user.is_admin)


@router.post("/logout/")
async def logout(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    payload = await decode_token(token)
    expires_at = datetime.fromtimestamp(payload.get("exp"))
    await RevokedTokenRepository.revoke_token(session, token, expires_at)
    return {"message": "Successfully logged out"}

