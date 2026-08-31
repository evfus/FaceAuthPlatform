from fastapi import Response
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.application import Application
from app.models.user_session import UserSession
from app.models.app_connection import AppConnection
from app.models.face_embedding import FaceEmbedding
from app.models.auth_code import AuthCode
from app.schemas.token import AuthResult
from app.core.security import generate_token, generate_auth_code, utcnow_naive

def get_or_create_user_session(user: User, db: Session, client_id: str = None) -> UserSession:
    existing = (
        db.query(UserSession)
        .filter(
            UserSession.user_id == user.id,
            UserSession.revoked == False,
            UserSession.expires_at > datetime.now(timezone.utc)
        ).first()
    )

    if existing:
        existing.expires_at = datetime.now(timezone.utc) + timedelta(hours = 24)
        if client_id is not None:
            existing.pending_client_id = client_id

        db.commit()
        db.refresh(existing)
        return existing
    
    return create_user_session(user, db, client_id)

def create_user_session(user: User, db: Session, client_id: str = None) -> UserSession:
    session = UserSession(
        token = generate_token(),
        user_id = user.id,
        expires_at = datetime.now(timezone.utc) + timedelta(hours = 24),
        pending_client_id = client_id,
    )

    db.add(session)
    db.commit()

    return session

def complete_login_or_signup(
    user: User,
    application: Application,
    response: Response,
    db: Session
) -> AuthResult:

    has_face = db.query(FaceEmbedding).filter(FaceEmbedding.user_id == user.id).first()

    if not has_face:
        session = get_or_create_user_session(user, db, application.client_id)
        set_session_cookie(response, session)

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
        application_id = application.id,
        expires_at = datetime.now(timezone.utc) + timedelta(minutes = 10)
    )
    
    session = get_or_create_user_session(user, db)
    set_session_cookie(response, session)

    db.add(auth_code)
    db.commit()
    
    return AuthResult(
        status = "authorized",
        session_token = session.token,
        session_expires_at = session.expires_at,
        redirect_url = f"{application.redirect_url}?code={code}"
    )

def set_session_cookie(response: Response, session: UserSession) -> None:
    max_age_seconds = int((session.expires_at - utcnow_naive()).total_seconds())
    response.set_cookie(
        key = "session_token",
        value = session.token,
        max_age = max_age_seconds,
        httponly = True,
        secure = False,
        samesite = "lax"
    )
