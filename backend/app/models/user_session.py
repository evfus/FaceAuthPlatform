from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class UserSession(Base):
    __tablename__ = "user_sessions"

    token = Column(String, primary_key = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    created_at = Column(DateTime, default = lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable = False)
    revoked = Column(Boolean, default = False)
    pending_client_id = Column(String, nullable = True)
