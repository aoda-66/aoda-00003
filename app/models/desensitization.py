from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base
from datetime import datetime

class DesensitizationRule(Base):
    __tablename__ = "desensitization_rule"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(50), nullable=False, index=True)
    column_name = Column(String(50), nullable=False, index=True)
    rule_type = Column(String(20), nullable=False)
    pattern = Column(String(200))
    replacement = Column(String(200))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)