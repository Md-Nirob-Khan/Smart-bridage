"""Pydantic request/response schemas."""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)  # bcrypt ignores bytes past 72
    # Self-registration cannot create admins; admins are seeded or promoted by an admin.
    role: Literal["engineer", "viewer"] = "viewer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------------- Bridges ----------------
class BridgeBase(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    location: str | None = Field(default=None, max_length=255)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    length_m: float | None = Field(default=None, gt=0)
    construction_year: int | None = Field(default=None, ge=1800, le=2100)
    bridge_type: str | None = Field(default=None, max_length=50)
    daily_traffic: int | None = Field(default=None, ge=0)
    last_inspection_date: date | None = None
    notes: str | None = None


class BridgeCreate(BridgeBase):
    pass


class BridgeUpdate(BridgeBase):
    pass


class BridgeOut(BridgeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
