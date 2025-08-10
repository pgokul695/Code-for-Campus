#!/usr/bin/env python3
"""
Database Seeding Script for Virtual Notice Board

This script populates the database with test data for development and testing.
It creates test users and notices with realistic data.
"""
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal, Base
from app.models.user import User
from app.models.notice import Notice

def create_test_users(db: Session):
    """Create test users in the database"""
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
        # Check if user already exists
        if not db.query(User).filter(User.uid == user_data["uid"]).first():
            db_user = User(**user_data)
            db.add(db_user)
    
    db.commit()
    print(f"Created {len(test_users)} test users")

def create_test_notices(db: Session):
    """Create test notices in the database"""
    now = datetime.utcnow()
    
    test_notices = [
        {
            "title": "Welcome to Virtual Notice Board",
            "content": "This is a test notice to demonstrate the Virtual Notice Board system. Please feel free to explore the features.",
            "category": "main",
            "subcategory": "announcement",
            "author_uid": "test_admin_1",
            "author_name": "Admin User",
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
            "author_uid": "test_admin_1",
            "author_name": "Admin User",
            "is_active": True,
            "priority": 1,
            "created_at": now - timedelta(hours=2),
            "expires_at": now + timedelta(days=2)
        }
    ]
    
    for notice_data in test_notices:
        # Check if notice with same title already exists
        if not db.query(Notice).filter(Notice.title == notice_data["title"]).first():
            db_notice = Notice(**notice_data)
            db.add(db_notice)
    
    db.commit()
    print(f"Created {len(test_notices)} test notices")

def main():
    """Main function to seed the database"""
    print("Starting database seeding...")
    
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        create_test_users(db)
        create_test_notices(db)
        print("Database seeding completed successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
