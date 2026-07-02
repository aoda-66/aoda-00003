from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Borrow(Base):
    __tablename__ = "borrow"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    borrow_code = Column(String(50), unique=True, nullable=False, index=True)
    collection_id = Column(Integer, ForeignKey("collection.id"), nullable=False, index=True)
    borrower_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    borrow_date = Column(DateTime, nullable=False)
    planned_return_date = Column(DateTime, nullable=False)
    actual_return_date = Column(DateTime)
    status = Column(String(20), default="pending", index=True)
    purpose = Column(Text)
    remarks = Column(Text)
    overdue_days = Column(Integer, default=0)
    is_overdue = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    collection = relationship("Collection", back_populates="borrows")
    borrower = relationship("User")
    approvals = relationship("BorrowApproval", back_populates="borrow", cascade="all, delete-orphan")
    
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_BORROWED = "borrowed"
    STATUS_RETURNED = "returned"
    STATUS_OVERDUE = "overdue"