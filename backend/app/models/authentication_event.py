from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime, timezone
from app.core.database import Base

class AuthenticationEvent(Base):
    __tablename__ = "authentication_events"

    id = Column(Integer, primary_key = True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable = False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    result = Column(String, nullable = False)
    confidence = Column(Float, nullable = True)
    reason = Column(String, nullable = True)
    created_at = Column(DateTime, default = lambda: datetime.now(timezone.utc))
