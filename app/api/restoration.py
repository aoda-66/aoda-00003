from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.crud.restoration import (
    get_restoration, get_restorations, get_restorations_by_collection, create_restoration, update_restoration, delete_restoration
)
from app.crud.user import get_user
from app.security.auth import check_permission
from app.schemas.restoration import RestorationCreate, RestorationUpdate, RestorationResponse
from app.models.user import User

router = APIRouter(prefix="/restorations", tags=["修复管理"])

@router.get("/", response_model=list[RestorationResponse])
async def read_restorations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
    is_completed: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("restoration_view"))
):
    restorations = get_restorations(db, skip=skip, limit=limit, status=status, is_completed=is_completed)
    return [
        RestorationResponse(
            id=r.id,
            restoration_code=r.restoration_code,
            collection_id=r.collection_id,
            status=r.status,
            description=r.description,
            method=r.method,
            materials=r.materials,
            before_condition=r.before_condition,
            after_condition=r.after_condition,
            operator_id=r.operator_id,
            operator_name=get_user(db, r.operator_id).real_name if r.operator_id else None,
            start_date=r.start_date,
            end_date=r.end_date,
            is_completed=r.is_completed,
            created_at=r.created_at,
            updated_at=r.updated_at
        )
        for r in restorations
    ]

@router.get("/collection/{collection_id}", response_model=list[RestorationResponse])
async def read_restorations_by_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("restoration_view"))
):
    restorations = get_restorations_by_collection(db, collection_id=collection_id)
    return [
        RestorationResponse(
            id=r.id,
            restoration_code=r.restoration_code,
            collection_id=r.collection_id,
            status=r.status,
            description=r.description,
            method=r.method,
            materials=r.materials,
            before_condition=r.before_condition,
            after_condition=r.after_condition,
            operator_id=r.operator_id,
            operator_name=get_user(db, r.operator_id).real_name if r.operator_id else None,
            start_date=r.start_date,
            end_date=r.end_date,
            is_completed=r.is_completed,
            created_at=r.created_at,
            updated_at=r.updated_at
        )
        for r in restorations
    ]

@router.get("/{restoration_id}", response_model=RestorationResponse)
async def read_restoration(
    restoration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("restoration_view"))
):
    restoration = get_restoration(db, restoration_id=restoration_id)
    if restoration is None:
        raise HTTPException(status_code=404, detail="修复记录不存在")
    return RestorationResponse(
        id=restoration.id,
        restoration_code=restoration.restoration_code,
        collection_id=restoration.collection_id,
        status=restoration.status,
        description=restoration.description,
        method=restoration.method,
        materials=restoration.materials,
        before_condition=restoration.before_condition,
        after_condition=restoration.after_condition,
        operator_id=restoration.operator_id,
        operator_name=get_user(db, restoration.operator_id).real_name if restoration.operator_id else None,
        start_date=restoration.start_date,
        end_date=restoration.end_date,
        is_completed=restoration.is_completed,
        created_at=restoration.created_at,
        updated_at=restoration.updated_at
    )

@router.post("/", response_model=RestorationResponse)
async def create_restoration_info(
    restoration: RestorationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("restoration_create"))
):
    result = create_restoration(db=db, restoration=restoration, operator_id=current_user.id)
    return RestorationResponse(
        id=result.id,
        restoration_code=result.restoration_code,
        collection_id=result.collection_id,
        status=result.status,
        description=result.description,
        method=result.method,
        materials=result.materials,
        before_condition=result.before_condition,
        after_condition=result.after_condition,
        operator_id=result.operator_id,
        operator_name=current_user.real_name,
        start_date=result.start_date,
        end_date=result.end_date,
        is_completed=result.is_completed,
        created_at=result.created_at,
        updated_at=result.updated_at
    )

@router.put("/{restoration_id}", response_model=RestorationResponse)
async def update_restoration_info(
    restoration_id: int,
    restoration_update: RestorationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("restoration_edit"))
):
    restoration = update_restoration(db, restoration_id=restoration_id, restoration_update=restoration_update)
    if restoration is None:
        raise HTTPException(status_code=404, detail="修复记录不存在")
    return RestorationResponse(
        id=restoration.id,
        restoration_code=restoration.restoration_code,
        collection_id=restoration.collection_id,
        status=restoration.status,
        description=restoration.description,
        method=restoration.method,
        materials=restoration.materials,
        before_condition=restoration.before_condition,
        after_condition=restoration.after_condition,
        operator_id=restoration.operator_id,
        operator_name=get_user(db, restoration.operator_id).real_name if restoration.operator_id else None,
        start_date=restoration.start_date,
        end_date=restoration.end_date,
        is_completed=restoration.is_completed,
        created_at=restoration.created_at,
        updated_at=restoration.updated_at
    )

@router.delete("/{restoration_id}")
async def delete_restoration_info(
    restoration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("restoration_delete"))
):
    success = delete_restoration(db, restoration_id=restoration_id)
    if not success:
        raise HTTPException(status_code=404, detail="修复记录不存在")
    return {"message": "删除成功"}