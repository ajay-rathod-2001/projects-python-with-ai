from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    mobile: Optional[str] = Field(None, max_length=20)
    password: str = Field(..., min_length=6, description="User password")
    full_name: str = Field(..., min_length=2, max_length=100)


class UserLogin(BaseModel):
    # User can login with email, username, or mobile
    identifier: str = Field(..., description="Email, username, or mobile number")
    password: str = Field(..., min_length=1)


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    username: Optional[str] = None
    mobile: Optional[str] = None
    full_name: str
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    user: UserOut
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
