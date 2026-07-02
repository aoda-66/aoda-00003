from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Image(Base):
    __tablename__ = "image"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey("collection.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    description = Column(String(200))
    is_primary = Column(Boolean, default=False)
    uploaded_by = Column(Integer, ForeignKey("user.id"))
    uploaded_at = Column(DateTime, default=datetime.now)
    
    collection = relationship("Collection", back_populates="images")