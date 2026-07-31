from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

from pydantic import BaseModel, EmailStr

class ProfileUpdate(BaseModel):
    username: str
    email: EmailStr

class ChangePassword(BaseModel):
    old_password: str
    new_password: str
