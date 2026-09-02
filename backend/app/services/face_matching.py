from dataclasses import dataclass
from typing import Optional
import numpy as np

from sqlalchemy.orm import Session

from app.models.face_embedding import FaceEmbedding
from app.models.user import User
from app.services.face_embedding import FaceEmbedder, bytes_to_embedding
from app.services.face_detection import FaceDetector
from app.core.config import settings

@dataclass
class MatchResult:
    matched: bool
    confidence: Optional[float]
    reason: Optional[str]

def match_face_to_user(
    frame: np.ndarray,
    user: User,
    db: Session,
    detector: FaceDetector,
    embedder: FaceEmbedder
) -> MatchResult:

    detected_faces = detector.detect(frame)
    if not detected_faces:
        return MatchResult(matched = False, confidence = None, reason = "no_face_detected")

    if len(detected_faces) > 1:
        return MatchResult(matched = False, confidence = None, reason = "multiple_faces_detected")

    live_face = detected_faces[0]
    live_embbeding = embedder.embed(frame, live_face)

    stored = (
        db.query(FaceEmbedding)
        .filter(FaceEmbedding.user_id == user.id)
        .all()
    )

    if not stored:
        return MatchResult(matched = False, confidence = None, reason = "no_enrolled_embeddings")

    best_score = -1.0

    for record in stored:
        stored_embedding = bytes_to_embedding(record.embedding)
        score = cosine_similarity(live_embbeding, stored_embedding)
        if score > best_score:
            best_score = score

    matched = best_score >= settings.face_match_threshold

    reason = None if matched else "below_threshold"

    return MatchResult(matched = matched, confidence = best_score, reason = reason)

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))



