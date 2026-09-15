from fastapi import Response
from sqlalchemy.orm import Session
from app.models.developer_session import DeveloperSession
from app.core.security import utcnow_naive, generate_token
from app.core.config import settings

def get_or_create_developer_session(developer_id: int, db: Session) -> DeveloperSession:
    session = (
        db.query(DeveloperSession)
        .filter(DeveloperSession.developer_id == developer_id, DeveloperSession.revoked == False)
        .first()
    )

    if session and session.expires_at > utcnow_naive():
        session.expires_at = utcnow_naive() + settings.session_lifetime
        db.commit()
        return session

    session = DeveloperSession(
        token = generate_token(),
        developer_id = developer_id,
        expires_at = utcnow_naive() + settings.session_lifetime,
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session

def set_developer_session_cookie(response: Response, session: DeveloperSession) -> None:
    max_age_seconds = int((session.expires_at - utcnow_naive()).total_seconds())
    response.set_cookie(
        key = "dev_session_token",
        value = session.token,
        max_age = max_age_seconds,
        httponly = True,
        secure = False,
        samesite = "lax"
    )
