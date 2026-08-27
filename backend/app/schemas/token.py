from pydantic import BaseModel
from datetime import datetime

class TokenRequest(BaseModel):
    code: str
    client_id: str
    client_secret: str

class TokenResponse(BaseModel):
    token: str
    expires_at: datetime
