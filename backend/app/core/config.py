from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    database_url: str = "sqlite:///./faceauth.db"

    face_detector_model: str = str(BASE_DIR / "ml_models" / "face_detection" / "face_detection_yunet.onnx")
    face_detector_confidence_threshold: float = 0.5

    class Config:
        env_file = ".env"

settings = Settings()
