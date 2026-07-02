from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.crud.collection import (
    get_collection, get_collections, create_collection, update_collection, delete_collection
)
from app.crud.user import get_user
from app.security.auth import check_permission
from app.schemas.collection import CollectionCreate, CollectionUpdate, CollectionResponse
from app.models.user import User

router = APIRouter(prefix="/collections", tags=["藏品管理"])

@router.get("/", response_model=list[CollectionResponse])
async def read_collections(
    skip: int = 0,
    limit: int = 100,
    search_keyword: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    era: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("collection_view"))
):
    collections = get_collections(
        db, skip=skip, limit=limit, search_keyword=search_keyword,
        category=category, era=era, location=location, is_public=is_public
    )
    return [
        CollectionResponse(
            id=c.id,
            collection_code=c.collection_code,
            name=c.name,
            category=c.category,
            era=c.era,
            origin=c.origin,
            material=c.material,
            size=c.size,
            weight=c.weight,
            condition=c.condition,
            description=c.description,
            location=c.location,
            owner_id=c.owner_id,
            owner_name=get_user(db, c.owner_id).real_name if c.owner_id else None,
            is_public=c.is_public,
            created_at=c.created_at,
            updated_at=c.updated_at
        )
        for c in collections
    ]

@router.get("/{collection_id}", response_model=CollectionResponse)
async def read_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("collection_view"))
):
    collection = get_collection(db, collection_id=collection_id)
    if collection is None:
        raise HTTPException(status_code=404, detail="藏品不存在")
    return CollectionResponse(
        id=collection.id,
        collection_code=collection.collection_code,
        name=collection.name,
        category=collection.category,
        era=collection.era,
        origin=collection.origin,
        material=collection.material,
        size=collection.size,
        weight=collection.weight,
        condition=collection.condition,
        description=collection.description,
        location=collection.location,
        owner_id=collection.owner_id,
        owner_name=get_user(db, collection.owner_id).real_name if collection.owner_id else None,
        is_public=collection.is_public,
        created_at=collection.created_at,
        updated_at=collection.updated_at
    )

@router.post("/", response_model=CollectionResponse)
async def create_collection_info(
    collection: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("collection_create"))
):
    db_collection = get_collection_by_code(db, collection_code=collection.collection_code)
    if db_collection:
        raise HTTPException(status_code=400, detail="藏品编号已存在")
    result = create_collection(db=db, collection=collection, owner_id=current_user.id)
    return CollectionResponse(
        id=result.id,
        collection_code=result.collection_code,
        name=result.name,
        category=result.category,
        era=result.era,
        origin=result.origin,
        material=result.material,
        size=result.size,
        weight=result.weight,
        condition=result.condition,
        description=result.description,
        location=result.location,
        owner_id=result.owner_id,
        owner_name=current_user.real_name,
        is_public=result.is_public,
        created_at=result.created_at,
        updated_at=result.updated_at
    )

@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection_info(
    collection_id: int,
    collection_update: CollectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("collection_edit"))
):
    collection = update_collection(db, collection_id=collection_id, collection_update=collection_update)
    if collection is None:
        raise HTTPException(status_code=404, detail="藏品不存在")
    return CollectionResponse(
        id=collection.id,
        collection_code=collection.collection_code,
        name=collection.name,
        category=collection.category,
        era=collection.era,
        origin=collection.origin,
        material=collection.material,
        size=collection.size,
        weight=collection.weight,
        condition=collection.condition,
        description=collection.description,
        location=collection.location,
        owner_id=collection.owner_id,
        owner_name=get_user(db, collection.owner_id).real_name if collection.owner_id else None,
        is_public=collection.is_public,
        created_at=collection.created_at,
        updated_at=collection.updated_at
    )

@router.delete("/{collection_id}")
async def delete_collection_info(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("collection_delete"))
):
    success = delete_collection(db, collection_id=collection_id)
    if not success:
        raise HTTPException(status_code=404, detail="藏品不存在")
    return {"message": "删除成功"}

from app.crud.collection import get_collection_by_code