from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    username: str
    email: EmailStr


class ChangePassword(BaseModel):
    old_password: str
    new_password: str
