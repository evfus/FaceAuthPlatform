from pydantic import BaseModel

class DeveloperAuthRequest(BaseModel):
    email: str
    password: str
