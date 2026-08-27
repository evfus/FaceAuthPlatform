from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Token(Base):
    __tablename__ = "tokens"

    token = Column(String, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False, index = True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable = False, index = True)
    expires_at = Column(DateTime, nullable = False)
    created_at = Column(DateTime, default = lambda: datetime.now(timezone.utc))

    user = relationship("User")
    application = relationship("Application")
