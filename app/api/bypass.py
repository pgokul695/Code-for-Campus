# bypass_simple.py - Minimal version with no external dependencies
# ⚠️ REMOVE THIS FILE AFTER TESTING! ⚠️

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import os
import hashlib

from ..database import get_db
from ..models.user import User
from ..models.notice import Notice  # <-- Ensure Notice model exists

router = APIRouter(prefix="/bypass", tags=["bypass"])

# --- Security Configuration ---
BYPASS_SECRET = os.getenv("BYPASS_SECRET", "railway-dev-bypass-2024")

# --- Reusable Dependency for Authentication ---
def verify_bypass_access(secret: str = Query(..., description="The bypass secret key")):
    """
    FastAPI dependency to verify bypass access with a secret from query parameters.
    Raises HTTPException if the secret is invalid.
    """
    if secret != BYPASS_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bypass secret"
        )

# --- Pydantic Models for Request Bodies ---
class PromoteUserPayload(BaseModel):
    user_id: int
    new_role: str

class CreateNoticePayload(BaseModel):
    title: str
    content: str
    category: str
    subcategory: str
    priority: int
    expires_at: datetime

# --- API Endpoints ---

@router.post("/instant-admin")
async def instant_admin_access(
    email: str = Query(..., description="Email of the user to create or promote to admin"),
    db: Session = Depends(get_db),
    _verified: None = Depends(verify_bypass_access)
):
    """
    🚨 RAILWAY BYPASS: Instantly become admin (Simple Version)
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        user = User(
            email=email,
            name=f"Admin User ({email})",
            role="admin",
            firebase_uid=f"bypass_{hashlib.md5(email.encode()).hexdigest()}",
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(user)
        action = "created"
    else:
        user.role = "admin"
        user.updated_at = datetime.utcnow()
        action = "promoted"
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User {action} as admin successfully",
        "user": {"id": user.id, "email": user.email, "name": user.name, "role": user.role},
        "next_steps": [
            "1. Use your regular login method (e.g., Firebase) to get a JWT token",
            "2. Your account now has the 'admin' role",
            "3. Access admin endpoints with your authenticated session"
        ]
    }

@router.post("/promote-user")
async def promote_existing_user(
    payload: PromoteUserPayload,
    db: Session = Depends(get_db),
    _verified: None = Depends(verify_bypass_access)
):
    """
    🚨 BYPASS: Promote any existing user to any role
    """
    if payload.new_role not in ["student", "faculty", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'student', 'faculty', or 'admin'"
        )
    
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {payload.user_id} not found"
        )
    
    old_role = user.role
    user.role = payload.new_role
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User promoted from '{old_role}' to '{payload.new_role}'",
        "user": {"id": user.id, "email": user.email, "name": user.name, "role": user.role}
    }

@router.get("/list-users")
async def list_users(
    db: Session = Depends(get_db),
    _verified: None = Depends(verify_bypass_access)
):
    """
    🚨 BYPASS: List all users to find IDs for promotion.
    """
    users = db.query(User).all()
    
    return {
        "total_users": len(users),
        "users": [
            {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "created_at": user.created_at
            }
            for user in users
        ]
    }

@router.post("/notices", summary="Create Notice")
async def create_notice(
    payload: CreateNoticePayload,
    db: Session = Depends(get_db),
    _verified: None = Depends(verify_bypass_access)
):
    """
    🚨 BYPASS: Create a new notice (no JWT required for testing)
    """
    notice = Notice(
        title=payload.title,
        content=payload.content,
        category=payload.category,
        subcategory=payload.subcategory,
        priority=payload.priority,
        expires_at=payload.expires_at,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        author_uid="bypass_admin",
        author_name="Bypass Admin"
    )

    db.add(notice)
    db.commit()
    db.refresh(notice)

    return {
        "id": notice.id,
        "author_uid": notice.author_uid,
        "author_name": notice.author_name,
        "is_active": notice.is_active,
        "created_at": notice.created_at,
        "updated_at": notice.updated_at,
        "title": notice.title,
        "content": notice.content,
        "category": notice.category,
        "subcategory": notice.subcategory,
        "priority": notice.priority,
        "expires_at": notice.expires_at
    }

@router.delete("/self-destruct")
async def self_destruct(
    confirm: str = Query(..., description="Must be 'YES-DELETE-BYPASS' to confirm."),
    _verified: None = Depends(verify_bypass_access)
):
    """
    🧨 SELF DESTRUCT: Provides instructions to disable bypass routes.
    """
    if confirm != "YES-DELETE-BYPASS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must confirm with 'YES-DELETE-BYPASS' in the confirm query parameter."
        )
    
    return {
        "message": "🧨 BYPASS SELF-DESTRUCT ACTIVATED",
        "instructions": [
            "1. Remove 'from .api import bypass_simple as bypass' from your main application file (e.g., main.py).",
            "2. Remove 'app.include_router(bypass.router, prefix=\"/api/v1\")' from your main application file.",
            "3. Delete this file: app/api/bypass_simple.py",
            "4. Redeploy your application."
        ],
        "status": "Ready for manual removal."
    }
