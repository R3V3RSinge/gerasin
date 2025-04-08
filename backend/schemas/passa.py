from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class PasswordEntryCreate(BaseModel):
    website: str = Field(..., max_length=255)
    username: Optional[str] = Field(None, max_length=255)
    password: str
    notes: Optional[str] = None

class PasswordEntryResponse(BaseModel):
    id_entry: int
    website: str
    username: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class PasswordEntryWithPasswordResponse(PasswordEntryResponse):
    password: str