from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TransferBase(BaseModel):
    transfer_type: str = Field(..., min_length=1, max_length=50)
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    description: Optional[str] = None
    transfer_date: Optional[datetime] = None

class TransferCreate(TransferBase):
    collection_id: int

class TransferUpdate(TransferBase):
    status: Optional[str] = None

class TransferResponse(TransferBase):
    id: int
    transfer_code: str
    collection_id: int
    status: str
    operator_id: Optional[int]
    operator_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True