from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.crud.transfer import (
    get_transfer, get_transfers, get_transfers_by_collection, create_transfer, update_transfer, delete_transfer
)
from app.crud.user import get_user
from app.security.auth import get_current_user, check_permission
from app.schemas.transfer import TransferCreate, TransferUpdate, TransferResponse
from app.models.user import User

router = APIRouter(prefix="/transfers", tags=["流转管理"])

@router.get("/", response_model=list[TransferResponse])
async def read_transfers(
    skip: int = 0,
    limit: int = 100,
    transfer_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transfers = get_transfers(db, skip=skip, limit=limit, transfer_type=transfer_type, status=status)
    return [
        TransferResponse(
            id=t.id,
            transfer_code=t.transfer_code,
            collection_id=t.collection_id,
            transfer_type=t.transfer_type,
            from_location=t.from_location,
            to_location=t.to_location,
            status=t.status,
            description=t.description,
            operator_id=t.operator_id,
            operator_name=get_user(db, t.operator_id).real_name if t.operator_id else None,
            transfer_date=t.transfer_date,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in transfers
    ]

@router.get("/collection/{collection_id}", response_model=list[TransferResponse])
async def read_transfers_by_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transfers = get_transfers_by_collection(db, collection_id=collection_id)
    return [
        TransferResponse(
            id=t.id,
            transfer_code=t.transfer_code,
            collection_id=t.collection_id,
            transfer_type=t.transfer_type,
            from_location=t.from_location,
            to_location=t.to_location,
            status=t.status,
            description=t.description,
            operator_id=t.operator_id,
            operator_name=get_user(db, t.operator_id).real_name if t.operator_id else None,
            transfer_date=t.transfer_date,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in transfers
    ]

@router.get("/{transfer_id}", response_model=TransferResponse)
async def read_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transfer = get_transfer(db, transfer_id=transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="流转记录不存在")
    return TransferResponse(
        id=transfer.id,
        transfer_code=transfer.transfer_code,
        collection_id=transfer.collection_id,
        transfer_type=transfer.transfer_type,
        from_location=transfer.from_location,
        to_location=transfer.to_location,
        status=transfer.status,
        description=transfer.description,
        operator_id=transfer.operator_id,
        operator_name=get_user(db, transfer.operator_id).real_name if transfer.operator_id else None,
        transfer_date=transfer.transfer_date,
        created_at=transfer.created_at,
        updated_at=transfer.updated_at
    )

@router.post("/", response_model=TransferResponse)
async def create_transfer_info(
    transfer: TransferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("transfer_create"))
):
    result = create_transfer(db=db, transfer=transfer, operator_id=current_user.id)
    return TransferResponse(
        id=result.id,
        transfer_code=result.transfer_code,
        collection_id=result.collection_id,
        transfer_type=result.transfer_type,
        from_location=result.from_location,
        to_location=result.to_location,
        status=result.status,
        description=result.description,
        operator_id=result.operator_id,
        operator_name=current_user.real_name,
        transfer_date=result.transfer_date,
        created_at=result.created_at,
        updated_at=result.updated_at
    )

@router.put("/{transfer_id}", response_model=TransferResponse)
async def update_transfer_info(
    transfer_id: int,
    transfer_update: TransferUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("transfer_edit"))
):
    transfer = update_transfer(db, transfer_id=transfer_id, transfer_update=transfer_update)
    if transfer is None:
        raise HTTPException(status_code=404, detail="流转记录不存在")
    return TransferResponse(
        id=transfer.id,
        transfer_code=transfer.transfer_code,
        collection_id=transfer.collection_id,
        transfer_type=transfer.transfer_type,
        from_location=transfer.from_location,
        to_location=transfer.to_location,
        status=transfer.status,
        description=transfer.description,
        operator_id=transfer.operator_id,
        operator_name=get_user(db, transfer.operator_id).real_name if transfer.operator_id else None,
        transfer_date=transfer.transfer_date,
        created_at=transfer.created_at,
        updated_at=transfer.updated_at
    )

@router.delete("/{transfer_id}")
async def delete_transfer_info(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("transfer_delete"))
):
    success = delete_transfer(db, transfer_id=transfer_id)
    if not success:
        raise HTTPException(status_code=404, detail="流转记录不存在")
    return {"message": "删除成功"}