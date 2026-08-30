from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class AppConnection(Base):
    __tablename__ = "app_connections"
    __table_args__ = (UniqueConstraint("application_id", "user_id", name = "uq_application_user"),)

    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable = False)
    created_at = Column(DateTime, default = lambda: datetime.now(timezone.utc))
