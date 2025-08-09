from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, User as UserSchema
from ..core.firebase import verify_firebase_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserSchema)
async def register_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # Verify Firebase token
    decoded_token = await verify_firebase_token(credentials.credentials)
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.uid == decoded_token["uid"]).first()
    if existing_user:
        return existing_user
    
    # Create new user
    user_data = UserCreate(
        uid=decoded_token["uid"],
        email=decoded_token.get("email", ""),
        name=decoded_token.get("name", decoded_token.get("email", "").split("@")[0])
    )
    
    db_user = User(**user_data.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
