from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional

class AuthResult(BaseModel):
    status: Literal["needs_enrollment", "authorized"]
    session_token: Optional[str] = None
    session_expires_at: Optional[datetime] = None
    redirect_url: Optional[str] = None

class TokenRequest(BaseModel):
    code: str
    client_id: str
    client_secret: str

class TokenResponse(BaseModel):
    token: str
    expires_at: datetime

class AuthorizeRequest(BaseModel):
    email: str
    password: str
