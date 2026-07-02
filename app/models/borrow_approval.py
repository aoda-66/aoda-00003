from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class BorrowApproval(Base):
    __tablename__ = "borrow_approval"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    borrow_id = Column(Integer, ForeignKey("borrow.id"), nullable=False, index=True)
    approver_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    approval_level = Column(Integer, nullable=False)
    status = Column(String(20), default="pending", index=True)
    comment = Column(Text)
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    
    borrow = relationship("Borrow", back_populates="approvals")
    approver = relationship("User")
    
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"