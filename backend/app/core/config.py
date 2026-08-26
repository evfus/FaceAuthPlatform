from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./faceauth.db"

    class Config:
        env_file = ".env"

settings = Settings()
