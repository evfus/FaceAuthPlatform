from pathlib import Path
from pydantic_settings import BaseSettings
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    database_url: str = "sqlite:///./faceauth.db"

    face_detector_model: str = str(BASE_DIR / "ml_models" / "face_detection" / "face_detection_yunet.onnx")
    face_detector_confidence_threshold: float = 0.5
    face_embedder_model: str = str(BASE_DIR / "ml_models" / "face_detection" / "face_recognition_sface.onnx")
    
    face_match_threshold: float = 0.4

    session_lifetime: timedelta = timedelta(hours = 24)

settings = Settings()
