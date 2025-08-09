from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NoticeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    category: str = Field(..., pattern="^(main|club|department)$")
    subcategory: Optional[str] = Field(None, max_length=100)
    priority: Optional[int] = Field(0, ge=0, le=10)
    expires_at: Optional[datetime] = None

class NoticeCreate(NoticeBase):
    pass

class NoticeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, pattern="^(main|club|department)$")
    subcategory: Optional[str] = Field(None, max_length=100)
    priority: Optional[int] = Field(None, ge=0, le=10)
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None

class Notice(BaseModel):
    id: int
    author_uid: str
    author_name: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    # Inherit NoticeBase fields
    title: str
    content: str
    category: str
    subcategory: Optional[str]
    priority: Optional[int]
    expires_at: Optional[datetime]
    class Config:
        from_attributes = True

class NoticeList(BaseModel):
    notices: list[Notice]
    total: int
    page: int
    per_page: int
    total_pages: int
