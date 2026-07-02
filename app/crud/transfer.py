from sqlalchemy.orm import Session
from app.models.transfer import Transfer
from app.schemas.transfer import TransferCreate, TransferUpdate
from typing import Optional, List
from datetime import datetime

def generate_transfer_code(db: Session) -> str:
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(Transfer).filter(Transfer.transfer_code.like(f"TF{today}%")).count() + 1
    return f"TF{today}{str(count).zfill(4)}"

def get_transfer(db: Session, transfer_id: int) -> Optional[Transfer]:
    return db.query(Transfer).filter(Transfer.id == transfer_id).first()

def get_transfers_by_collection(db: Session, collection_id: int) -> List[Transfer]:
    return db.query(Transfer).filter(Transfer.collection_id == collection_id).all()

def get_transfers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    transfer_type: Optional[str] = None,
    status: Optional[str] = None
) -> List[Transfer]:
    query = db.query(Transfer)
    
    if transfer_type:
        query = query.filter(Transfer.transfer_type == transfer_type)
    
    if status:
        query = query.filter(Transfer.status == status)
    
    return query.order_by(Transfer.created_at.desc()).offset(skip).limit(limit).all()

def create_transfer(db: Session, transfer: TransferCreate, operator_id: int) -> Transfer:
    db_transfer = Transfer(
        **transfer.dict(),
        transfer_code=generate_transfer_code(db),
        operator_id=operator_id
    )
    db.add(db_transfer)
    db.commit()
    db.refresh(db_transfer)
    return db_transfer

def update_transfer(db: Session, transfer_id: int, transfer_update: TransferUpdate) -> Optional[Transfer]:
    db_transfer = get_transfer(db, transfer_id)
    if not db_transfer:
        return None
    for key, value in transfer_update.dict(exclude_unset=True).items():
        setattr(db_transfer, key, value)
    db.commit()
    db.refresh(db_transfer)
    return db_transfer

def delete_transfer(db: Session, transfer_id: int) -> bool:
    db_transfer = get_transfer(db, transfer_id)
    if not db_transfer:
        return False
    db.delete(db_transfer)
    db.commit()
    return True