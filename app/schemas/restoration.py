from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RestorationBase(BaseModel):
    description: Optional[str] = None
    method: Optional[str] = None
    materials: Optional[str] = None
    before_condition: Optional[str] = None
    after_condition: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class RestorationCreate(RestorationBase):
    collection_id: int

class RestorationUpdate(RestorationBase):
    status: Optional[str] = None
    is_completed: Optional[bool] = None

class RestorationResponse(RestorationBase):
    id: int
    restoration_code: str
    collection_id: int
    status: str
    operator_id: Optional[int]
    operator_name: Optional[str] = None
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True