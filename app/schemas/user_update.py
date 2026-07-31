from pydantic import BaseModel, EmailStr

class UserUpdate(BaseModel):
    username: str
    email: EmailStr
