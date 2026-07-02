from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Transfer(Base):
    __tablename__ = "transfer"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey("collection.id"), nullable=False, index=True)
    transfer_code = Column(String(50), unique=True, nullable=False, index=True)
    transfer_type = Column(String(50), nullable=False)
    from_location = Column(String(100))
    to_location = Column(String(100))
    status = Column(String(20), default="pending")
    description = Column(Text)
    operator_id = Column(Integer, ForeignKey("user.id"))
    transfer_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    collection = relationship("Collection", back_populates="transfers")