from sqlalchemy.orm import Session
from app.models.image import Image
from app.schemas.image import ImageCreate, ImageUpdate
from typing import Optional, List

def get_image(db: Session, image_id: int) -> Optional[Image]:
    return db.query(Image).filter(Image.id == image_id).first()

def get_images_by_collection(db: Session, collection_id: int) -> List[Image]:
    return db.query(Image).filter(Image.collection_id == collection_id).all()

def get_images(db: Session, skip: int = 0, limit: int = 100) -> List[Image]:
    return db.query(Image).order_by(Image.uploaded_at.desc()).offset(skip).limit(limit).all()

def create_image(db: Session, image: ImageCreate, uploaded_by: int) -> Image:
    db_image = Image(
        **image.dict(),
        uploaded_by=uploaded_by
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def update_image(db: Session, image_id: int, image_update: ImageUpdate) -> Optional[Image]:
    db_image = get_image(db, image_id)
    if not db_image:
        return None
    for key, value in image_update.dict(exclude_unset=True).items():
        setattr(db_image, key, value)
    db.commit()
    db.refresh(db_image)
    return db_image

def delete_image(db: Session, image_id: int) -> bool:
    db_image = get_image(db, image_id)
    if not db_image:
        return False
    db.delete(db_image)
    db.commit()
    return True