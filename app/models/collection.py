from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Collection(Base):
    __tablename__ = "collection"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    era = Column(String(50))
    origin = Column(String(100))
    material = Column(String(50))
    size = Column(String(100))
    weight = Column(Float)
    condition = Column(String(50))
    description = Column(Text)
    location = Column(String(100))
    owner_id = Column(Integer, ForeignKey("user.id"))
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    diseases = relationship("Disease", back_populates="collection", cascade="all, delete-orphan")
    restorations = relationship("Restoration", back_populates="collection", cascade="all, delete-orphan")
    patrols = relationship("Patrol", back_populates="collection", cascade="all, delete-orphan")
    images = relationship("Image", back_populates="collection", cascade="all, delete-orphan")
    transfers = relationship("Transfer", back_populates="collection", cascade="all, delete-orphan")