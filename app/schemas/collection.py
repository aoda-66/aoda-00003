from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CollectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = None
    era: Optional[str] = None
    origin: Optional[str] = None
    material: Optional[str] = None
    size: Optional[str] = None
    weight: Optional[float] = None
    condition: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    is_public: Optional[bool] = True

class CollectionCreate(CollectionBase):
    collection_code: str = Field(..., min_length=1, max_length=50)

class CollectionUpdate(CollectionBase):
    collection_code: Optional[str] = None

class CollectionResponse(CollectionBase):
    id: int
    collection_code: str
    owner_id: Optional[int]
    owner_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True