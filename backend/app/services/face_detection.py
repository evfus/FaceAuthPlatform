import cv2
import numpy as np
from dataclasses import dataclass
from app.core.config import settings

@dataclass
class DetectedFace:
    x: int
    y: int
    width: int
    height: int
    confidence: float

class FaceDetector:
    def __init__(self):
        self.detector = cv2.FaceDetectorYN.create(
            settings.face_detector_model,
            "",
            (0, 0),
            score_threshold = settings.face_detector_confidence_threshold
        )

    def detect(self, image: np.ndarray) -> list[DetectedFace]:
        h, w = image.shape[:2]
        self.detector.setInputSize((w, h))

        _, faces = self.detector.detect(image)

        results = []

        if faces is None:
            return results

        for face in faces:
            x, y, width, height = face[0:4].astype(int)
            confidence = face[:-1].astype(float)

            x = max(0, min(x, w))
            y = max(0, min(y, h))
            x2 = max(0, min(x + width, w))
            y2 = max(0, min(y + height, h))

            if x2 <= x or y2 <= y:
                continue

            results.append(DetectedFace(
                x = x,
                y = y,
                width = x2 - x,
                height = y2 - y,
                confidence = confidence
            ))

        return results
