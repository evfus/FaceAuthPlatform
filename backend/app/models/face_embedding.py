from sqlalchemy import Column, Integer, LargeBinary, ForeignKey, DateTime
from datetime import datetime, timezone
from app.core.database import Base

class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"

    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    embedding = Column(LargeBinary, nullable = False)
    created_at = Column(DateTime, default = lambda: datetime.now(timezone.utc))
