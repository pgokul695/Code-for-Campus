# bypass_simple.py - Minimal version with no external dependencies
# ⚠️ REMOVE THIS FILE AFTER TESTING! ⚠️

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
import os
import hashlib

from ..database import get_db
from ..models.user import User

router = APIRouter(prefix="/bypass", tags=["bypass"])

# Security measures
BYPASS_SECRET = os.getenv("BYPASS_SECRET", "railway-dev-bypass-2024")

def verify_bypass_access(request: Request, secret: str):
    """Verify bypass access with secret"""
    
    # Check secret
    if secret != BYPASS_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bypass secret"
        )
    
    return True

@router.post("/instant-admin")
async def instant_admin_access(
    email: str,
    secret: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    🚨 RAILWAY BYPASS: Instantly become admin (Simple Version)
    
    This creates/promotes user to admin without JWT token generation
    After this, use regular login flow to get tokens
    
    Usage:
    POST /api/v1/bypass/instant-admin
    {
        "email": "your-email@domain.com",
        "secret": "your-bypass-secret"
    }
    
    ⚠️ REMOVE THIS ENDPOINT AFTER SETUP! ⚠️
    """
    verify_bypass_access(request, secret)
    
    # Find or create user
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Create new admin user
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
        # Promote existing user
        user.role = "admin"
        user.updated_at = datetime.utcnow()
        action = "promoted"
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User {action} as admin successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        },
        "next_steps": [
            "1. Use your regular login method (Firebase) to get JWT token",
            "2. Your account now has admin role",
            "3. Access admin endpoints with your authenticated session"
        ]
    }

@router.post("/emergency-admin")
async def emergency_admin(
    request: Request,
    secret: str,
    db: Session = Depends(get_db)
):
    """
    🚨 ULTIMATE BYPASS: Creates emergency admin without email requirement
    
    Creates admin user: emergency@railway.dev
    Password: Use Firebase auth or your regular login flow
    
    Use this if you have no existing users!
    """
    verify_bypass_access(request, secret)
    
    emergency_email = "emergency@railway.dev"
    
    # Check if emergency admin already exists
    existing = db.query(User).filter(User.email == emergency_email).first()
    if existing and existing.role == "admin":
        return {
            "message": "Emergency admin already exists",
            "user": {
                "id": existing.id,
                "email": existing.email,
                "role": existing.role
            },
            "instructions": "Use regular login flow with this email to get admin access"
        }
    
    # Create or promote emergency admin
    if existing:
        existing.role = "admin"
        existing.updated_at = datetime.utcnow()
        user = existing
    else:
        user = User(
            email=emergency_email,
            name="Emergency Admin",
            role="admin",
            firebase_uid="emergency_admin_railway",
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Emergency admin created successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        },
        "instructions": [
            "1. Set up Firebase authentication for emergency@railway.dev",
            "2. Login using your regular authentication flow", 
            "3. You now have admin access",
            "⚠️ Change this after setup! Delete this endpoint!"
        ]
    }

@router.post("/promote-user")
async def promote_existing_user(
    user_id: int,
    secret: str,
    new_role: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    🚨 BYPASS: Promote any existing user to any role
    
    Usage:
    POST /api/v1/bypass/promote-user
    {
        "user_id": 123,
        "new_role": "admin",
        "secret": "your-bypass-secret"
    }
    """
    verify_bypass_access(request, secret)
    
    if new_role not in ["student", "faculty", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'student', 'faculty', or 'admin'"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    old_role = user.role
    user.role = new_role
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User promoted from '{old_role}' to '{new_role}'",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }

@router.get("/list-users")
async def list_users(
    secret: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    🚨 BYPASS: List all users to find IDs
    """
    verify_bypass_access(request, secret)
    
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

@router.get("/status")
async def bypass_status(request: Request):
    """Check if bypass routes are active"""
    return {
        "status": "🚨 SIMPLE BYPASS ROUTES ACTIVE 🚨",
        "warning": "These routes should be removed in production!",
        "your_ip": request.client.host,
        "endpoints": [
            "POST /bypass/instant-admin",
            "POST /bypass/emergency-admin",
            "POST /bypass/promote-user",
            "GET /bypass/list-users"
        ],
        "note": "This version doesn't generate JWT tokens - use regular login after promotion"
    }

@router.delete("/self-destruct")
async def self_destruct(
    secret: str,
    confirm: str,
    request: Request
):
    """
    🧨 SELF DESTRUCT: Disable bypass routes
    """
    verify_bypass_access(request, secret)
    
    if confirm != "YES-DELETE-BYPASS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must confirm with 'YES-DELETE-BYPASS'"
        )
    
    return {
        "message": "🧨 BYPASS SELF-DESTRUCT ACTIVATED",
        "instructions": [
            "1. Remove 'from .api import bypass' from main.py",
            "2. Remove 'app.include_router(bypass.router, prefix=\"/api/v1\")' from main.py", 
            "3. Delete app/api/bypass.py file",
            "4. Redeploy your application"
        ],
        "status": "Ready for removal"
    }
