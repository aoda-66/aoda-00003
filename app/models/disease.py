from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Disease(Base):
    __tablename__ = "disease"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey("collection.id"), nullable=False, index=True)
    disease_type = Column(String(50), nullable=False)
    severity = Column(String(20))
    area = Column(Float)
    location = Column(String(100))
    description = Column(Text)
    recorded_by = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    collection = relationship("Collection", back_populates="diseases")