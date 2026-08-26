from datetime import datetime
from pydantic import BaseModel

class ApplicationCreate(BaseModel):
    name: str
    redirect_url: str

class ApplicationResponse(BaseModel):
    id: int
    name: str
    client_id: str
    redirect_url: str
    created_at: datetime
    
    class config:
        from_attributes = True

class ApplicationCreateResponse(ApplicationResponse):
    client_secret: str

