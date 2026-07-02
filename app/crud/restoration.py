from sqlalchemy.orm import Session
from app.models.restoration import Restoration
from app.schemas.restoration import RestorationCreate, RestorationUpdate
from typing import Optional, List
from datetime import datetime

def generate_restoration_code(db: Session) -> str:
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(Restoration).filter(Restoration.restoration_code.like(f"RX{today}%")).count() + 1
    return f"RX{today}{str(count).zfill(4)}"

def get_restoration(db: Session, restoration_id: int) -> Optional[Restoration]:
    return db.query(Restoration).filter(Restoration.id == restoration_id).first()

def get_restorations_by_collection(db: Session, collection_id: int) -> List[Restoration]:
    return db.query(Restoration).filter(Restoration.collection_id == collection_id).all()

def get_restorations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    is_completed: Optional[bool] = None
) -> List[Restoration]:
    query = db.query(Restoration)
    
    if status:
        query = query.filter(Restoration.status == status)
    
    if is_completed is not None:
        query = query.filter(Restoration.is_completed == is_completed)
    
    return query.order_by(Restoration.created_at.desc()).offset(skip).limit(limit).all()

def create_restoration(db: Session, restoration: RestorationCreate, operator_id: int) -> Restoration:
    db_restoration = Restoration(
        **restoration.dict(),
        restoration_code=generate_restoration_code(db),
        operator_id=operator_id
    )
    db.add(db_restoration)
    db.commit()
    db.refresh(db_restoration)
    return db_restoration

def update_restoration(db: Session, restoration_id: int, restoration_update: RestorationUpdate) -> Optional[Restoration]:
    db_restoration = get_restoration(db, restoration_id)
    if not db_restoration:
        return None
    for key, value in restoration_update.dict(exclude_unset=True).items():
        setattr(db_restoration, key, value)
    db.commit()
    db.refresh(db_restoration)
    return db_restoration

def delete_restoration(db: Session, restoration_id: int) -> bool:
    db_restoration = get_restoration(db, restoration_id)
    if not db_restoration:
        return False
    db.delete(db_restoration)
    db.commit()
    return True