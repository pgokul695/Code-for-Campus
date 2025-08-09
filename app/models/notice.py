from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from ..database import Base

class Notice(Base):
    __tablename__ = "notices"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)  # main, club, department
    subcategory = Column(String(100), index=True)  # specific club/department name
    author_uid = Column(String(128), nullable=False)
    author_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher number = higher priority
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
