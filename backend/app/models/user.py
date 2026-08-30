from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime, timezone
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key = True)
    email = Column(String, nullable = False, index = True)
    password_hash = Column(String, nullable = False)
    created_at = Column(DateTime, default = lambda: datetime.now(timezone.utc))
