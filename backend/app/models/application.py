from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, nullable = False)
    client_id = Column(String, unique = True, nullable = False, index = True)
    client_secret_hash = Column(String, nullable = False)
    redirect_url = Column(String, nullable = False)
    created_at = Column(DateTime(timezone = True), server_default = func.now())
