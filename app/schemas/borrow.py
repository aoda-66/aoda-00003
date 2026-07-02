from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class BorrowBase(BaseModel):
    collection_id: int
    borrow_date: datetime
    planned_return_date: datetime
    purpose: Optional[str] = None
    remarks: Optional[str] = None

class BorrowCreate(BorrowBase):
    pass

class BorrowUpdate(BaseModel):
    status: Optional[str] = None
    actual_return_date: Optional[datetime] = None
    remarks: Optional[str] = None

class BorrowResponse(BorrowBase):
    id: int
    borrow_code: str
    borrower_id: int
    borrower_name: Optional[str] = None
    collection_name: Optional[str] = None
    collection_code: Optional[str] = None
    status: str
    actual_return_date: Optional[datetime] = None
    overdue_days: int
    is_overdue: bool
    reminder_sent: bool
    current_approval_level: Optional[int] = None
    next_approver_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class BorrowApprovalBase(BaseModel):
    borrow_id: int
    approver_id: int
    approval_level: int

class BorrowApprovalCreate(BorrowApprovalBase):
    pass

class BorrowApprovalUpdate(BaseModel):
    status: str
    comment: Optional[str] = None

class BorrowApprovalResponse(BorrowApprovalBase):
    id: int
    status: str
    comment: Optional[str] = None
    approver_name: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class OverdueReportResponse(BaseModel):
    borrow_id: int
    borrow_code: str
    collection_name: str
    collection_code: str
    borrower_name: str
    borrow_date: datetime
    planned_return_date: datetime
    actual_return_date: Optional[datetime] = None
    overdue_days: int
    status: str
    created_at: datetime

class ReminderNotificationResponse(BaseModel):
    borrow_id: int
    borrow_code: str
    collection_name: str
    borrower_name: str
    planned_return_date: datetime
    days_until_due: int
    status: str