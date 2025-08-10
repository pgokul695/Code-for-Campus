# bypass.py - Add this to your app/api/ directory
# ⚠️ REMOVE THIS FILE AFTER TESTING! ⚠️

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import os
import hashlib

from ..database import get_db
from ..models.user import User
from ..core.security import create_access_token

router = APIRouter(prefix="/bypass", tags=["bypass"])

# Security measures even for bypass
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
    🚨 RAILWAY BYPASS: Instantly become admin with token generation
    
    This creates/promotes user to admin AND returns a valid JWT token
    
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
    
    # Generate JWT token (valid for 7 days for testing)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": "admin"},
        expires_delta=timedelta(days=7)
    )
    
    return {
        "message": f"User {action} as admin successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        },
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 7 * 24 * 3600,  # 7 days in seconds
        "usage": {
            "header": f"Authorization: Bearer {access_token}",
            "curl_example": f"curl -H 'Authorization: Bearer {access_token}' http://your-app.railway.app/api/v1/admin/users"
        }
    }

@router.get("/admin-token")
async def get_admin_token(
    email: str,
    secret: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    🚨 RAILWAY BYPASS: Get admin token for existing admin user
    
    Usage: GET /api/v1/bypass/admin-token?email=admin@domain.com&secret=your-secret
    """
    verify_bypass_access(request, secret)
    
    user = db.query(User).filter(User.email == email, User.role == "admin").first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found. Use /instant-admin to create one."
        )
    
    # Generate fresh token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": "admin"},
        expires_delta=timedelta(days=7)
    )
    
    return {
        "message": "Admin token generated",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        },
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 7 * 24 * 3600
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
    Password: Not needed (token-based)
    
    Use this if you have no existing users!
    """
    verify_bypass_access(request, secret)
    
    emergency_email = "emergency@railway.dev"
    
    # Check if emergency admin already exists
    existing = db.query(User).filter(User.email == emergency_email).first()
    if existing and existing.role == "admin":
        # Generate token for existing emergency admin
        access_token = create_access_token(
            data={"sub": existing.email, "user_id": existing.id, "role": "admin"},
            expires_delta=timedelta(days=7)
        )
        
        return {
            "message": "Emergency admin already exists",
            "user": {
                "id": existing.id,
                "email": existing.email,
                "role": existing.role
            },
            "access_token": access_token,
            "token_type": "bearer"
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
    
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": "admin"},
        expires_delta=timedelta(days=7)
    )
    
    return {
        "message": "Emergency admin created successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        },
        "access_token": access_token,
        "token_type": "bearer",
        "warning": "⚠️ Change this after setup! Delete this endpoint!"
    }

@router.get("/status")
async def bypass_status(request: Request):
    """Check if bypass routes are active"""
    return {
        "status": "🚨 BYPASS ROUTES ACTIVE 🚨",
        "warning": "These routes should be removed in production!",
        "your_ip": request.client.host,
        "endpoints": [
            "POST /bypass/instant-admin",
            "GET /bypass/admin-token", 
            "POST /bypass/emergency-admin"
        ],
        "env_vars": {
            "BYPASS_SECRET": "Required - set your secret"
        }
    }

@router.delete("/self-destruct")
async def self_destruct(
    secret: str,
    confirm: str,
    request: Request
):
    """
    🧨 SELF DESTRUCT: Disable bypass routes
    
    This doesn't delete the file but returns code to remove the router
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
        "code_to_remove": """
# Remove these lines from main.py:
from .api import bypass
app.include_router(bypass.router, prefix="/api/v1")
        """,
        "status": "Ready for removal"
    }
