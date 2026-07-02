from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.crud.disease import (
    get_disease, get_diseases, get_diseases_by_collection, create_disease, update_disease, delete_disease
)
from app.crud.user import get_user
from app.security.auth import get_current_user, check_permission
from app.schemas.disease import DiseaseCreate, DiseaseUpdate, DiseaseResponse
from app.models.user import User

router = APIRouter(prefix="/diseases", tags=["病害管理"])

@router.get("/", response_model=list[DiseaseResponse])
async def read_diseases(
    skip: int = 0,
    limit: int = 100,
    disease_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    diseases = get_diseases(db, skip=skip, limit=limit, disease_type=disease_type, severity=severity)
    return [
        DiseaseResponse(
            id=d.id,
            collection_id=d.collection_id,
            disease_type=d.disease_type,
            severity=d.severity,
            area=d.area,
            location=d.location,
            description=d.description,
            recorded_by=d.recorded_by,
            recorded_by_name=get_user(db, d.recorded_by).real_name if d.recorded_by else None,
            created_at=d.created_at,
            updated_at=d.updated_at
        )
        for d in diseases
    ]

@router.get("/collection/{collection_id}", response_model=list[DiseaseResponse])
async def read_diseases_by_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    diseases = get_diseases_by_collection(db, collection_id=collection_id)
    return [
        DiseaseResponse(
            id=d.id,
            collection_id=d.collection_id,
            disease_type=d.disease_type,
            severity=d.severity,
            area=d.area,
            location=d.location,
            description=d.description,
            recorded_by=d.recorded_by,
            recorded_by_name=get_user(db, d.recorded_by).real_name if d.recorded_by else None,
            created_at=d.created_at,
            updated_at=d.updated_at
        )
        for d in diseases
    ]

@router.get("/{disease_id}", response_model=DiseaseResponse)
async def read_disease(
    disease_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    disease = get_disease(db, disease_id=disease_id)
    if disease is None:
        raise HTTPException(status_code=404, detail="病害记录不存在")
    return DiseaseResponse(
        id=disease.id,
        collection_id=disease.collection_id,
        disease_type=disease.disease_type,
        severity=disease.severity,
        area=disease.area,
        location=disease.location,
        description=disease.description,
        recorded_by=disease.recorded_by,
        recorded_by_name=get_user(db, disease.recorded_by).real_name if disease.recorded_by else None,
        created_at=disease.created_at,
        updated_at=disease.updated_at
    )

@router.post("/", response_model=DiseaseResponse)
async def create_disease_info(
    disease: DiseaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("disease_create"))
):
    result = create_disease(db=db, disease=disease, recorded_by=current_user.id)
    return DiseaseResponse(
        id=result.id,
        collection_id=result.collection_id,
        disease_type=result.disease_type,
        severity=result.severity,
        area=result.area,
        location=result.location,
        description=result.description,
        recorded_by=result.recorded_by,
        recorded_by_name=current_user.real_name,
        created_at=result.created_at,
        updated_at=result.updated_at
    )

@router.put("/{disease_id}", response_model=DiseaseResponse)
async def update_disease_info(
    disease_id: int,
    disease_update: DiseaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("disease_edit"))
):
    disease = update_disease(db, disease_id=disease_id, disease_update=disease_update)
    if disease is None:
        raise HTTPException(status_code=404, detail="病害记录不存在")
    return DiseaseResponse(
        id=disease.id,
        collection_id=disease.collection_id,
        disease_type=disease.disease_type,
        severity=disease.severity,
        area=disease.area,
        location=disease.location,
        description=disease.description,
        recorded_by=disease.recorded_by,
        recorded_by_name=get_user(db, disease.recorded_by).real_name if disease.recorded_by else None,
        created_at=disease.created_at,
        updated_at=disease.updated_at
    )

@router.delete("/{disease_id}")
async def delete_disease_info(
    disease_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("disease_delete"))
):
    success = delete_disease(db, disease_id=disease_id)
    if not success:
        raise HTTPException(status_code=404, detail="病害记录不存在")
    return {"message": "删除成功"}