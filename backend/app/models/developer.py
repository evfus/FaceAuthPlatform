from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.core.database import Base

class Developer(Base):
    __tablename__ = "developers"

    id = Column(Integer, primary_key = True)
    email = Column(String, unique = True, index = True, nullable = False)
    password_hash = Column(String, nullable = False)
    created_at = Column(DateTime, default = datetime.now(timezone.utc))
