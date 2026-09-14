from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime, timezone
from app.core.database import Base

class DeveloperSession(Base):
    __tablename__ = "developer_sessions"

    token = Column(String, primary_key = True, index = True)
    developer_id = Column(Integer, ForeignKey("developers.id"), nullable = False)
    expires_at = Column(DateTime, nullable = False)
    revoked = Column(Boolean, default = False)
    created_at = Column(DateTime, default = datetime.now(timezone.utc))

