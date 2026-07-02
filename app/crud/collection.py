from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.collection import Collection
from app.models.user import User
from app.schemas.collection import CollectionCreate, CollectionUpdate
from typing import Optional, List

def get_collection(db: Session, collection_id: int) -> Optional[Collection]:
    return db.query(Collection).filter(Collection.id == collection_id).first()

def get_collection_by_code(db: Session, collection_code: str) -> Optional[Collection]:
    return db.query(Collection).filter(Collection.collection_code == collection_code).first()

def get_collections(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search_keyword: Optional[str] = None,
    category: Optional[str] = None,
    era: Optional[str] = None,
    location: Optional[str] = None,
    is_public: Optional[bool] = None
) -> List[Collection]:
    query = db.query(Collection)
    
    if search_keyword:
        query = query.filter(
            or_(
                Collection.name.contains(search_keyword),
                Collection.collection_code.contains(search_keyword),
                Collection.description.contains(search_keyword)
            )
        )
    
    if category:
        query = query.filter(Collection.category == category)
    
    if era:
        query = query.filter(Collection.era == era)
    
    if location:
        query = query.filter(Collection.location == location)
    
    if is_public is not None:
        query = query.filter(Collection.is_public == is_public)
    
    return query.order_by(Collection.created_at.desc()).offset(skip).limit(limit).all()

def create_collection(db: Session, collection: CollectionCreate, owner_id: int) -> Collection:
    db_collection = Collection(
        **collection.dict(),
        owner_id=owner_id
    )
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return db_collection

def update_collection(db: Session, collection_id: int, collection_update: CollectionUpdate) -> Optional[Collection]:
    db_collection = get_collection(db, collection_id)
    if not db_collection:
        return None
    for key, value in collection_update.dict(exclude_unset=True).items():
        setattr(db_collection, key, value)
    db.commit()
    db.refresh(db_collection)
    return db_collection

def delete_collection(db: Session, collection_id: int) -> bool:
    db_collection = get_collection(db, collection_id)
    if not db_collection:
        return False
    db.delete(db_collection)
    db.commit()
    return True

def get_collection_count(db: Session) -> int:
    return db.query(Collection).count()