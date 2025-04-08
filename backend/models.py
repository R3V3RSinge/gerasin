from datetime import datetime


from sqlalchemy import String, Boolean, DateTime, ForeignKey, LargeBinary, Text
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id_user: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)


class PasswordEntry(Base):
    __tablename__ = "password_entries"

    id_entry: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_user: Mapped[int] = mapped_column(ForeignKey("users.id_user"))
    website: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(255))
    encrypted_password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    notes: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User")