from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Restoration(Base):
    __tablename__ = "restoration"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey("collection.id"), nullable=False, index=True)
    restoration_code = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(String(20), default="pending")
    description = Column(Text)
    method = Column(String(200))
    materials = Column(String(200))
    before_condition = Column(Text)
    after_condition = Column(Text)
    operator_id = Column(Integer, ForeignKey("user.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    collection = relationship("Collection", back_populates="restorations")