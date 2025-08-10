"""
Development utilities API endpoints.
These endpoints are for development and testing purposes only.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..database import get_db
from ..models.user import User
from ..models.notice import Notice

router = APIRouter()
security = HTTPBearer()

@router.post("/init-test-data", status_code=status.HTTP_201_CREATED)
async def init_test_data(db: Session = Depends(get_db)):
    """
    Initialize the database with test data.
    WARNING: This will add test users and notices to the database.
    """
    try:
        # Create test users
        test_users = [
            {
                "uid": "pgokul695+admin",
                "email": "pgokul695+admin@example.com",
                "name": "Gokul Admin",
                "role": "admin",
                "department": "Administration",
                "is_active": True
            },
            {
                "uid": "test_admin_1",
                "email": "admin@test.com",
                "name": "Admin User",
                "role": "admin",
                "department": "Administration",
                "is_active": True
            },
            {
                "uid": "test_faculty_1",
                "email": "faculty@test.com",
                "name": "Faculty Member",
                "role": "faculty",
                "department": "Computer Science",
                "is_active": True
            },
            {
                "uid": "test_student_1",
                "email": "student@test.com",
                "name": "Test Student",
                "role": "student",
                "department": "Computer Science",
                "is_active": True
            }
        ]
        
        for user_data in test_users:
            if not db.query(User).filter(User.uid == user_data["uid"]).first():
                db_user = User(**user_data)
                db.add(db_user)
        
        db.commit()
        
        # Create test notices
        now = datetime.utcnow()
        test_notices = [
            {
                "title": "Welcome to Virtual Notice Board",
                "content": "This is a test notice to demonstrate the Virtual Notice Board system. Please feel free to explore the features.",
                "category": "main",
                "subcategory": "announcement",
                "author_uid": "pgokul695+admin",
                "author_name": "Gokul Admin",
                "is_active": True,
                "priority": 1,
                "created_at": now - timedelta(days=2),
                "expires_at": now + timedelta(days=30)
            },
            {
                "title": "Coding Competition 2023",
                "content": "Annual coding competition is scheduled for next month. Register now to participate!",
                "category": "department",
                "subcategory": "Computer Science",
                "author_uid": "test_faculty_1",
                "author_name": "Faculty Member",
                "is_active": True,
                "priority": 2,
                "created_at": now - timedelta(days=1),
                "expires_at": now + timedelta(days=14)
            },
            {
                "title": "Sports Week Announcement",
                "content": "Sports week will be held from next Monday. All students are encouraged to participate.",
                "category": "club",
                "subcategory": "Sports Club",
                "author_uid": "test_faculty_1",
                "author_name": "Faculty Member",
                "is_active": True,
                "priority": 1,
                "created_at": now - timedelta(hours=6),
                "expires_at": now + timedelta(days=7)
            },
            {
                "title": "Library Maintenance",
                "content": "The central library will be closed for maintenance this weekend. Plan your studies accordingly.",
                "category": "main",
                "subcategory": "announcement",
                "author_uid": "pgokul695+admin",
                "author_name": "Gokul Admin",
                "is_active": True,
                "priority": 1,
                "created_at": now - timedelta(hours=2),
                "expires_at": now + timedelta(days=2)
            }
        ]
        
        for notice_data in test_notices:
            if not db.query(Notice).filter(Notice.title == notice_data["title"]).first():
                db_notice = Notice(**notice_data)
                db.add(db_notice)
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Test data initialized successfully",
            "users_added": len(test_users),
            "notices_added": len(test_notices)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing test data: {str(e)}"
        )
