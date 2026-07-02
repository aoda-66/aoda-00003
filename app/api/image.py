from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
from uuid import uuid4
import aiofiles
from app.core.database import get_db
from app.core.config import settings
from app.crud.image import (
    get_image, get_images, get_images_by_collection, create_image, update_image, delete_image
)
from app.crud.user import get_user
from app.security.auth import get_current_user, check_permission
from app.schemas.image import ImageCreate, ImageUpdate, ImageResponse
from app.models.user import User

router = APIRouter(prefix="/images", tags=["影像管理"])

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "bmp", "tiff", "obj", "ply", "stl"}

async def save_uploaded_file(file: UploadFile, collection_id: int) -> str:
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不支持的文件格式")
    
    storage_dir = Path(settings.IMAGE_STORAGE_DIR) / str(collection_id)
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    unique_filename = f"{uuid4()}.{file_ext}"
    file_path = storage_dir / unique_filename
    
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    
    return str(file_path)

@router.get("/", response_model=list[ImageResponse])
async def read_images(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    images = get_images(db, skip=skip, limit=limit)
    return [
        ImageResponse(
            id=i.id,
            collection_id=i.collection_id,
            file_name=i.file_name,
            file_path=i.file_path,
            file_type=i.file_type,
            file_size=i.file_size,
            description=i.description,
            is_primary=i.is_primary,
            uploaded_by=i.uploaded_by,
            uploaded_by_name=get_user(db, i.uploaded_by).real_name if i.uploaded_by else None,
            uploaded_at=i.uploaded_at
        )
        for i in images
    ]

@router.get("/collection/{collection_id}", response_model=list[ImageResponse])
async def read_images_by_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    images = get_images_by_collection(db, collection_id=collection_id)
    return [
        ImageResponse(
            id=i.id,
            collection_id=i.collection_id,
            file_name=i.file_name,
            file_path=i.file_path,
            file_type=i.file_type,
            file_size=i.file_size,
            description=i.description,
            is_primary=i.is_primary,
            uploaded_by=i.uploaded_by,
            uploaded_by_name=get_user(db, i.uploaded_by).real_name if i.uploaded_by else None,
            uploaded_at=i.uploaded_at
        )
        for i in images
    ]

@router.get("/{image_id}", response_model=ImageResponse)
async def read_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    image = get_image(db, image_id=image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="影像不存在")
    return ImageResponse(
        id=image.id,
        collection_id=image.collection_id,
        file_name=image.file_name,
        file_path=image.file_path,
        file_type=image.file_type,
        file_size=image.file_size,
        description=image.description,
        is_primary=image.is_primary,
        uploaded_by=image.uploaded_by,
        uploaded_by_name=get_user(db, image.uploaded_by).real_name if image.uploaded_by else None,
        uploaded_at=image.uploaded_at
    )

@router.post("/")
async def upload_image(
    collection_id: int,
    file: UploadFile = File(...),
    description: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("image_upload"))
):
    file_path = await save_uploaded_file(file, collection_id)
    file_size = len(await file.read())
    
    image_create = ImageCreate(
        collection_id=collection_id,
        file_name=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=file_size,
        description=description
    )
    
    result = create_image(db=db, image=image_create, uploaded_by=current_user.id)
    return ImageResponse(
        id=result.id,
        collection_id=result.collection_id,
        file_name=result.file_name,
        file_path=result.file_path,
        file_type=result.file_type,
        file_size=result.file_size,
        description=result.description,
        is_primary=result.is_primary,
        uploaded_by=result.uploaded_by,
        uploaded_by_name=current_user.real_name,
        uploaded_at=result.uploaded_at
    )

@router.put("/{image_id}", response_model=ImageResponse)
async def update_image_info(
    image_id: int,
    image_update: ImageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("image_edit"))
):
    image = update_image(db, image_id=image_id, image_update=image_update)
    if image is None:
        raise HTTPException(status_code=404, detail="影像不存在")
    return ImageResponse(
        id=image.id,
        collection_id=image.collection_id,
        file_name=image.file_name,
        file_path=image.file_path,
        file_type=image.file_type,
        file_size=image.file_size,
        description=image.description,
        is_primary=image.is_primary,
        uploaded_by=image.uploaded_by,
        uploaded_by_name=get_user(db, image.uploaded_by).real_name if image.uploaded_by else None,
        uploaded_at=image.uploaded_at
    )

@router.delete("/{image_id}")
async def delete_image_info(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("image_delete"))
):
    image = get_image(db, image_id=image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="影像不存在")
    
    file_path = Path(image.file_path)
    if file_path.exists():
        file_path.unlink()
    
    success = delete_image(db, image_id=image_id)
    if not success:
        raise HTTPException(status_code=404, detail="影像不存在")
    return {"message": "删除成功"}