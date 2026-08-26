from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable = False, index = True)
    username = Column(String, nullable = False)
    created_at = Column(DateTime, default = lambda: datetime.now(timezone.utc))

    application = relationship("Application", back_populates = "users")
