from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, nullable = False)
    client_id = Column(String, unique = True, nullable = False, index = True)
    client_secret_hash = Column(String, nullable = False)
    redirect_url = Column(String, nullable = False)
    created_at = Column(DateTime, default = lambda: datetime.now(timezone.utc))

    users = relationship("User", back_populates = "application")
