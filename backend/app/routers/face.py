import cv2
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_user_from_session
from app.schemas.token import AuthResult
from app.models.user import User
from app.models.application import Application
from app.models.user_session import UserSession
from app.models.face_embedding import FaceEmbedding
from app.services.face_detection import FaceDetector
from app.services.face_embedding import FaceEmbedder, embedding_to_bytes
from app.services.auth_flow import complete_login_or_signup

router = APIRouter(prefix = "/face", tags = ["face"])

@router.post("/enroll", response_model = AuthResult)
def enroll_face(
    response: Response,
    files: list[UploadFile] = File(...),
    current: tuple[User, UserSession] = Depends(get_user_from_session),
    db: Session = Depends(get_db)
):

    user, session = current

    detector = FaceDetector()
    embedder = FaceEmbedder()

    new_embeddings = []

    for upload in files:
        contents = upload.file.read()
        image_array = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code = 400, detail = f"Could not decode image: {upload.filename}")

        faces = detector.detect(image)
        
        if len(faces) < 1:
            raise HTTPException(status_code = 400, detail = "No face detected")
        if len(faces) > 1:
            raise HTTPException(status_code = 400, detail = "Multiple faces detected")

        embedding = embedder.embed(image, faces[0])
        new_embeddings.append(embedding_to_bytes(embedding))

    db.query(FaceEmbedding).filter(FaceEmbedding.user_id == user.id).delete()

    for emb_bytes in new_embeddings:
        db.add(FaceEmbedding(user_id = user.id, embedding = emb_bytes))

    db.commit()

    if session.pending_client_id:
        application = db.query(Application).filter(Application.client_id == session.pending_client_id).first()
        result = complete_login_or_signup(user, application, response, db)

        session.pending_client_id = None

        db.commit()

        return result
    
    return AuthResult(status = "authorized")

