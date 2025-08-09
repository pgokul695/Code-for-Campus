from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import Optional
from datetime import datetime
import math

from ..database import get_db
from ..models.notice import Notice
from ..models.user import User
from ..schemas.notice import NoticeCreate, NoticeUpdate, Notice as NoticeSchema, NoticeList
from ..core.security import get_current_user, get_current_admin, get_current_user_optional

router = APIRouter()

@router.get("/", response_model=NoticeList)
async def get_notices(
    category: Optional[str] = Query(None, regex="^(main|club|department)$"),
    subcategory: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    include_expired: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    query = db.query(Notice).filter(Notice.is_active == True)
    
    # Filter by expiration
    if not include_expired:
        now = datetime.utcnow()
        query = query.filter(or_(Notice.expires_at.is_(None), Notice.expires_at > now))
    
    # Filter by category
    if category:
        query = query.filter(Notice.category == category)
    
    # Filter by subcategory
    if subcategory:
        query = query.filter(Notice.subcategory == subcategory)
    
    # Search functionality
    if search:
        search_filter = or_(
            Notice.title.ilike(f"%{search}%"),
            Notice.content.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Count total records
    total = query.count()
    
    # Apply pagination and ordering
    query = query.order_by(desc(Notice.priority), desc(Notice.created_at))
    offset = (page - 1) * per_page
    notices = query.offset(offset).limit(per_page).all()
    
    total_pages = math.ceil(total / per_page)
    
    return NoticeList(
        notices=notices,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@router.post("/", response_model=NoticeSchema)
async def create_notice(
    notice: NoticeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    db_notice = Notice(
        **notice.dict(),
        author_uid=current_user.uid,
        author_name=current_user.name
    )
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return db_notice

@router.get("/{notice_id}", response_model=NoticeSchema)
async def get_notice(
    notice_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    
    # Check if notice is expired (unless user is admin)
    if (notice.expires_at and notice.expires_at < datetime.utcnow() and 
        (not current_user or current_user.role != "admin")):
        raise HTTPException(status_code=404, detail="Notice not found")
    
    return notice

@router.put("/{notice_id}", response_model=NoticeSchema)
async def update_notice(
    notice_id: int,
    notice_update: NoticeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    
    update_data = notice_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(notice, field, value)
    
    db.commit()
    db.refresh(notice)
    return notice

@router.delete("/{notice_id}")
async def delete_notice(
    notice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    
    db.delete(notice)
    db.commit()
    return {"message": "Notice deleted successfully"}

@router.get("/categories/subcategories")
async def get_subcategories(
    category: str = Query(..., regex="^(main|club|department)$"),
    db: Session = Depends(get_db)
):
    subcategories = db.query(Notice.subcategory).filter(
        and_(Notice.category == category, Notice.subcategory.isnot(None))
    ).distinct().all()
    
    return {"subcategories": [sub[0] for sub in subcategories if sub[0]]}
