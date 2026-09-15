"""Pydantic schemas for User create, read, update, and authentication.

Matches the SQLAlchemy User model in app.models.user:
- id: int
- username: str
- email: EmailStr
- password: str (hashed in database, excluded from read schemas)
- phone_number: Optional[str]
- device_id: Optional[str]
- notifications_enabled: bool
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """Shared base properties for User."""
    username: str
    email: EmailStr
    phone_number: Optional[str] = None
    device_id: Optional[str] = None
    notifications_enabled: bool = True


class UserCreate(BaseModel):
    """Schema for registering or creating a new User."""
    username: str
    email: EmailStr
    password: str
    phone_number: Optional[str] = None
    device_id: Optional[str] = None
    notifications_enabled: Optional[bool] = True


class UserUpdate(BaseModel):
    """Schema for updating an existing User (supports partial updates)."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone_number: Optional[str] = None
    device_id: Optional[str] = None
    notifications_enabled: Optional[bool] = None


class UserRead(UserBase):
    """Schema for serializing and returning User data (excludes password)."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# UserResponse alias for backward-compatibility with existing routes
UserResponse = UserRead


class UserLogin(BaseModel):
    """Schema for user authentication credentials."""
    email: EmailStr
    password: str


class ProfileUpdate(BaseModel):
    """Schema for user self-profile updates."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    device_id: Optional[str] = None
    notifications_enabled: Optional[bool] = None


class ChangePassword(BaseModel):
    """Schema for updating password."""
    old_password: str
    new_password: str
