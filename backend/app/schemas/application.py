from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator

class ApplicationCreate(BaseModel):
    name: str
    redirect_url: str

    @field_validator("name", "redirect_url")
    @classmethod
    def if_not_empty_string(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Must not be empty")
        return v

class UpdateApplicationRequest(BaseModel):
    name: str | None = None
    redirect_url: str | None = None

    @field_validator("name", "redirect_url")
    @classmethod
    def if_not_empty_string(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Must not be empty")
        return v

class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: int
    name: str
    client_id: str
    redirect_url: str
    created_at: datetime

class ApplicationCreateResponse(ApplicationResponse):
    client_secret: str

