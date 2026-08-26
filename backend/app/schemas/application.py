from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ApplicationCreate(BaseModel):
    name: str
    redirect_url: str

class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: int
    name: str
    client_id: str
    redirect_url: str
    created_at: datetime

class ApplicationCreateResponse(ApplicationResponse):
    client_secret: str

