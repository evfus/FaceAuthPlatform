from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FaceLoginRequest(BaseModel):
    email: str
    client_id: str
    redirect_url: str

class FaceLoginResponse(BaseModel):
    matched: bool
    confidence: Optional[float] = None
    reason: Optional[str] = None
    session_token: Optional[str] = None
    session_expires_at: Optional[datetime] = None
    redirect_url: Optional[str] = None

