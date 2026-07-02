from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ImageBase(BaseModel):
    file_name: str = Field(..., min_length=1)
    file_path: str = Field(..., min_length=1)
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    description: Optional[str] = None
    is_primary: Optional[bool] = False

class ImageCreate(ImageBase):
    collection_id: int

class ImageUpdate(BaseModel):
    description: Optional[str] = None
    is_primary: Optional[bool] = None

class ImageResponse(ImageBase):
    id: int
    collection_id: int
    uploaded_by: Optional[int]
    uploaded_by_name: Optional[str] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True