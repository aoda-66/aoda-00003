from sqlalchemy.orm import Session
from app.models.disease import Disease
from app.schemas.disease import DiseaseCreate, DiseaseUpdate
from typing import Optional, List

def get_disease(db: Session, disease_id: int) -> Optional[Disease]:
    return db.query(Disease).filter(Disease.id == disease_id).first()

def get_diseases_by_collection(db: Session, collection_id: int) -> List[Disease]:
    return db.query(Disease).filter(Disease.collection_id == collection_id).all()

def get_diseases(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    disease_type: Optional[str] = None,
    severity: Optional[str] = None
) -> List[Disease]:
    query = db.query(Disease)
    
    if disease_type:
        query = query.filter(Disease.disease_type == disease_type)
    
    if severity:
        query = query.filter(Disease.severity == severity)
    
    return query.order_by(Disease.created_at.desc()).offset(skip).limit(limit).all()

def create_disease(db: Session, disease: DiseaseCreate, recorded_by: int) -> Disease:
    db_disease = Disease(
        **disease.dict(),
        recorded_by=recorded_by
    )
    db.add(db_disease)
    db.commit()
    db.refresh(db_disease)
    return db_disease

def update_disease(db: Session, disease_id: int, disease_update: DiseaseUpdate) -> Optional[Disease]:
    db_disease = get_disease(db, disease_id)
    if not db_disease:
        return None
    for key, value in disease_update.dict(exclude_unset=True).items():
        setattr(db_disease, key, value)
    db.commit()
    db.refresh(db_disease)
    return db_disease

def delete_disease(db: Session, disease_id: int) -> bool:
    db_disease = get_disease(db, disease_id)
    if not db_disease:
        return False
    db.delete(db_disease)
    db.commit()
    return True