import cv2
import numpy as np
from app.core.config import settings
from app.services.face_detection import DetectedFace

class FaceEmbedder():
    def __init__(self):
        self.embedder = cv2.FaceRecognizerSF.create(
            settings.face_embedder_model,
            ""
        )

    def embed(self, image: np.ndarray, face: DetectedFace) -> np.ndarray:
        face_box = np.array([[
            face.x, face.y, face.width, face.height,
            *face.landmarks.flatten(), face.confidence
        ]],
        dtype = np.float32)

        aligned_face = self.embedder.alignCrop(image, face_box)
        embedding = self.embedder.feature(aligned_face)

        return embedding.flatten()

def embedding_to_bytes(embedding: np.ndarray) -> bytes:
    return embedding.astype(np.float32).tobytes()

def bytes_to_embedding(data: bytes) -> np.ndarray:
    return np.frombuffer(data, dtype = np.float23)
