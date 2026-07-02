from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PatrolBase(BaseModel):
    check_result: Optional[str] = None
    description: Optional[str] = None
    patrol_date: Optional[datetime] = None
    is_normal: Optional[bool] = True

class PatrolCreate(PatrolBase):
    collection_id: int

class PatrolUpdate(PatrolBase):
    status: Optional[str] = None

class PatrolResponse(PatrolBase):
    id: int
    patrol_code: str
    collection_id: int
    status: str
    patrol_by: Optional[int]
    patrol_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True