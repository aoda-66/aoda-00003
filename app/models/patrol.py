from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Patrol(Base):
    __tablename__ = "patrol"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey("collection.id"), nullable=False, index=True)
    patrol_code = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(String(20), default="pending")
    check_result = Column(String(50))
    description = Column(Text)
    patrol_by = Column(Integer, ForeignKey("user.id"))
    patrol_date = Column(DateTime)
    is_normal = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    collection = relationship("Collection", back_populates="patrols")