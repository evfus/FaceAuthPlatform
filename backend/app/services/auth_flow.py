from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.application import Application
from app.models.user_session import UserSession
from app.models.app_connection import AppConnection
from app.models.face_embedding import FaceEmbedding
from app.models.auth_code import AuthCode
from app.schemas.token import AuthResult
from app.core.security import generate_token, generate_auth_code

def create_user_session(user: User, db: Session, client_id: str = None, redirect_url: str = None) -> UserSession:
    session = UserSession(
        token = generate_token(),
        user_id = user.id,
        expires_at = datetime.now(timezone.utc) + timedelta(hours = 24),
        pending_client_id = client_id,
        pending_redirect_url = redirect_url
    )

    db.add(session)
    db.commit()

    return session

def complete_login_or_signup(user: User, application: Application, db: Session) -> AuthResult:
    has_face = db.query(FaceEmbedding).filter(FaceEmbedding.user_id == user.id).first()

    if not has_face:
        session = create_user_session(user, db, application.client_id, application.redirect_url)
        
        return AuthResult(
            status = "needs_enrollment",
            session_token = session.token,
            session_expires_at = session.expires_at
        )
    
    connection = (
        db.query(AppConnection)
        .filter(AppConnection.user_id == user.id, AppConnection.application_id == application.id)
        .first()
    )

    if not connection:
        db.add(AppConnection(user_id = user.id, application_id = application.id))

    code = generate_auth_code()
    auth_code = AuthCode(
        code = code,
        user_id = user.id,
        applcation_id = application.id,
        expires_at = datetime.now(timezone.utc) + timedelta(minutes = 10)
    )

    db.add(auth_code)
    db.commit()
    
    return AuthResult(
        status = "authorized",
        redirect_url = f"{application.redirect_url}?code={code}"
    )
