from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str = "student"
    department: Optional[str] = None

class UserCreate(UserBase):
    uid: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    uid: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    class Config:
        from_attributes = True
