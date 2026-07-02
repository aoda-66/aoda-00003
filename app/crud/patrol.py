from sqlalchemy.orm import Session
from app.models.patrol import Patrol
from app.schemas.patrol import PatrolCreate, PatrolUpdate
from typing import Optional, List
from datetime import datetime

def generate_patrol_code(db: Session) -> str:
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(Patrol).filter(Patrol.patrol_code.like(f"PT{today}%")).count() + 1
    return f"PT{today}{str(count).zfill(4)}"

def get_patrol(db: Session, patrol_id: int) -> Optional[Patrol]:
    return db.query(Patrol).filter(Patrol.id == patrol_id).first()

def get_patrols_by_collection(db: Session, collection_id: int) -> List[Patrol]:
    return db.query(Patrol).filter(Patrol.collection_id == collection_id).all()

def get_patrols(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    is_normal: Optional[bool] = None
) -> List[Patrol]:
    query = db.query(Patrol)
    
    if status:
        query = query.filter(Patrol.status == status)
    
    if is_normal is not None:
        query = query.filter(Patrol.is_normal == is_normal)
    
    return query.order_by(Patrol.created_at.desc()).offset(skip).limit(limit).all()

def create_patrol(db: Session, patrol: PatrolCreate, patrol_by: int) -> Patrol:
    db_patrol = Patrol(
        **patrol.dict(),
        patrol_code=generate_patrol_code(db),
        patrol_by=patrol_by
    )
    db.add(db_patrol)
    db.commit()
    db.refresh(db_patrol)
    return db_patrol

def update_patrol(db: Session, patrol_id: int, patrol_update: PatrolUpdate) -> Optional[Patrol]:
    db_patrol = get_patrol(db, patrol_id)
    if not db_patrol:
        return None
    for key, value in patrol_update.dict(exclude_unset=True).items():
        setattr(db_patrol, key, value)
    db.commit()
    db.refresh(db_patrol)
    return db_patrol

def delete_patrol(db: Session, patrol_id: int) -> bool:
    db_patrol = get_patrol(db, patrol_id)
    if not db_patrol:
        return False
    db.delete(db_patrol)
    db.commit()
    return True