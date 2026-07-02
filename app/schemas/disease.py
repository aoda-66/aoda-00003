from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DiseaseBase(BaseModel):
    disease_type: str = Field(..., min_length=1, max_length=50)
    severity: Optional[str] = None
    area: Optional[float] = None
    location: Optional[str] = None
    description: Optional[str] = None

class DiseaseCreate(DiseaseBase):
    collection_id: int

class DiseaseUpdate(DiseaseBase):
    pass

class DiseaseResponse(DiseaseBase):
    id: int
    collection_id: int
    recorded_by: Optional[int]
    recorded_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True