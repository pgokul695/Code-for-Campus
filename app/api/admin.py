# admin.py - Add this to your app/api/ directory

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.user import User
from ..models.notice import Notice
from ..schemas.user import UserResponse, UserCreate, UserUpdate, AdminUserResponse
from ..schemas.notice import NoticeResponse
from ..core.security import get_current_user, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])

# Admin-only decorator
def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# User Management Routes
@router.get("/users", response_model=List[AdminUserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(admin_required)
):
    """Get all users (admin only)"""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(admin_required)
):
    """Get specific user by ID (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(admin_required)
):
    """Update user role (admin only)"""
    if new_role not in ["student", "faculty", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'student', 'faculty', or 'admin'"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.role = new_role
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return {"message": f"User role updated to {new_role}", "user": user}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(admin_required)
):
    """Delete user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete admin users"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

# Notice Management Routes
@router.get("/notices", response_model=List[NoticeResponse])
async def get_all_notices_admin(
    skip: int = 0,
    limit: int = 100,
    include_expired: bool = True,
    db: Session = Depends(get_db),
    admin_user: User = Depends(admin_required)
):
    """Get all notices including expired ones (admin only)"""
    query = db.query(Notice)
    
    if not include_expired:
        query = query.filter(Notice.expires_at > datetime.utcnow())
    
    notices = query.offset(skip).limit(limit).all()
    return notices

@router.put("/notices/{notice_id}/approve")
async def approve_notice(
    notice_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(admin_required)
):
    """Approve a pending notice (admin only)"""
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notice not found"
        )
    
    notice.is_approved = True
    notice.approved_by = admin_user.id
    notice.approved_at = datetime.utcnow()
    notice.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(notice)
    
    return {"message": "Notice approved successfully", "notice": notice}

@router.put("/notices/{notice_id}/reject")
async def reject_notice(
    notice_id: int,
    reason: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(admin_required)
):
    """Reject a pending notice (admin only)"""
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notice not found"
        )
    
    notice.is_approved = False
    notice.rejection_reason = reason
    notice.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(notice)
    
    return {"message": "Notice rejected successfully", "notice": notice}

@router.delete("/notices/{notice_id}")
async def delete_notice_admin(
    notice_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(admin_required)
):
    """Delete any notice (admin only)"""
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notice not found"
        )
    
    db.delete(notice)
    db.commit()
    
    return {"message": "Notice deleted successfully"}

# System Statistics
@router.get("/stats")
async def get_system_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(admin_required)
):
    """Get system statistics (admin only)"""
    total_users = db.query(User).count()
    total_notices = db.query(Notice).count()
    pending_notices = db.query(Notice).filter(Notice.is_approved == None).count()
    approved_notices = db.query(Notice).filter(Notice.is_approved == True).count()
    
    users_by_role = {}
    for role in ["student", "faculty", "admin"]:
        users_by_role[role] = db.query(User).filter(User.role == role).count()
    
    return {
        "total_users": total_users,
        "total_notices": total_notices,
        "pending_notices": pending_notices,
        "approved_notices": approved_notices,
        "users_by_role": users_by_role,
        "generated_at": datetime.utcnow()
    }

# Bulk Operations
@router.post("/notices/bulk-approve")
async def bulk_approve_notices(
    notice_ids: List[int],
    db: Session = Depends(get_db),
    admin_user: User = Depends(admin_required)
):
    """Bulk approve multiple notices (admin only)"""
    notices = db.query(Notice).filter(Notice.id.in_(notice_ids)).all()
    
    if not notices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No notices found with provided IDs"
        )
    
    approved_count = 0
    for notice in notices:
        if notice.is_approved is None:  # Only approve pending notices
            notice.is_approved = True
            notice.approved_by = admin_user.id
            notice.approved_at = datetime.utcnow()
            notice.updated_at = datetime.utcnow()
            approved_count += 1
    
    db.commit()
    
    return {
        "message": f"Approved {approved_count} notices",
        "approved_count": approved_count,
        "total_requested": len(notice_ids)
    }
