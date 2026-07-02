from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.crud.patrol import (
    get_patrol, get_patrols, get_patrols_by_collection, create_patrol, update_patrol, delete_patrol
)
from app.crud.user import get_user
from app.security.auth import get_current_user, check_permission
from app.schemas.patrol import PatrolCreate, PatrolUpdate, PatrolResponse
from app.models.user import User

router = APIRouter(prefix="/patrols", tags=["巡护管理"])

@router.get("/", response_model=list[PatrolResponse])
async def read_patrols(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
    is_normal: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patrols = get_patrols(db, skip=skip, limit=limit, status=status, is_normal=is_normal)
    return [
        PatrolResponse(
            id=p.id,
            patrol_code=p.patrol_code,
            collection_id=p.collection_id,
            status=p.status,
            check_result=p.check_result,
            description=p.description,
            patrol_by=p.patrol_by,
            patrol_by_name=get_user(db, p.patrol_by).real_name if p.patrol_by else None,
            patrol_date=p.patrol_date,
            is_normal=p.is_normal,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in patrols
    ]

@router.get("/collection/{collection_id}", response_model=list[PatrolResponse])
async def read_patrols_by_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patrols = get_patrols_by_collection(db, collection_id=collection_id)
    return [
        PatrolResponse(
            id=p.id,
            patrol_code=p.patrol_code,
            collection_id=p.collection_id,
            status=p.status,
            check_result=p.check_result,
            description=p.description,
            patrol_by=p.patrol_by,
            patrol_by_name=get_user(db, p.patrol_by).real_name if p.patrol_by else None,
            patrol_date=p.patrol_date,
            is_normal=p.is_normal,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in patrols
    ]

@router.get("/{patrol_id}", response_model=PatrolResponse)
async def read_patrol(
    patrol_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patrol = get_patrol(db, patrol_id=patrol_id)
    if patrol is None:
        raise HTTPException(status_code=404, detail="巡护记录不存在")
    return PatrolResponse(
        id=patrol.id,
        patrol_code=patrol.patrol_code,
        collection_id=patrol.collection_id,
        status=patrol.status,
        check_result=patrol.check_result,
        description=patrol.description,
        patrol_by=patrol.patrol_by,
        patrol_by_name=get_user(db, patrol.patrol_by).real_name if patrol.patrol_by else None,
        patrol_date=patrol.patrol_date,
        is_normal=patrol.is_normal,
        created_at=patrol.created_at,
        updated_at=patrol.updated_at
    )

@router.post("/", response_model=PatrolResponse)
async def create_patrol_info(
    patrol: PatrolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("patrol_create"))
):
    result = create_patrol(db=db, patrol=patrol, patrol_by=current_user.id)
    return PatrolResponse(
        id=result.id,
        patrol_code=result.patrol_code,
        collection_id=result.collection_id,
        status=result.status,
        check_result=result.check_result,
        description=result.description,
        patrol_by=result.patrol_by,
        patrol_by_name=current_user.real_name,
        patrol_date=result.patrol_date,
        is_normal=result.is_normal,
        created_at=result.created_at,
        updated_at=result.updated_at
    )

@router.put("/{patrol_id}", response_model=PatrolResponse)
async def update_patrol_info(
    patrol_id: int,
    patrol_update: PatrolUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("patrol_edit"))
):
    patrol = update_patrol(db, patrol_id=patrol_id, patrol_update=patrol_update)
    if patrol is None:
        raise HTTPException(status_code=404, detail="巡护记录不存在")
    return PatrolResponse(
        id=patrol.id,
        patrol_code=patrol.patrol_code,
        collection_id=patrol.collection_id,
        status=patrol.status,
        check_result=patrol.check_result,
        description=patrol.description,
        patrol_by=patrol.patrol_by,
        patrol_by_name=get_user(db, patrol.patrol_by).real_name if patrol.patrol_by else None,
        patrol_date=patrol.patrol_date,
        is_normal=patrol.is_normal,
        created_at=patrol.created_at,
        updated_at=patrol.updated_at
    )

@router.delete("/{patrol_id}")
async def delete_patrol_info(
    patrol_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("patrol_delete"))
):
    success = delete_patrol(db, patrol_id=patrol_id)
    if not success:
        raise HTTPException(status_code=404, detail="巡护记录不存在")
    return {"message": "删除成功"}