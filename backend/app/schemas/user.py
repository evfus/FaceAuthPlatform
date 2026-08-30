from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserRegister(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: int
    email: str
    created_at: datetime

