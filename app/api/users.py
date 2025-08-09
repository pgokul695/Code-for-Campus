from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, User as UserSchema
from ..core.security import get_current_user, get_current_admin

router = APIRouter()

@router.post("/", response_model=UserSchema)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    # Check if user already exists
    existing_user = db.query(User).filter(User.uid == user.uid).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered")
    
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Update last login
    current_user.last_login = datetime.utcnow()
    db.commit()
    return current_user

@router.put("/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_data = user_update.dict(exclude_unset=True)
    
    # Students can't change their own role
    if current_user.role != "admin" and "role" in update_data:
        del update_data["role"]
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/", response_model=list[UserSchema])
async def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return db.query(User).all()

@router.put("/{user_uid}", response_model=UserSchema)
async def update_user(
    user_uid: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.uid == user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user
