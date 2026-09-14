from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import utcnow_naive
from app.core.config import settings
from app.models.developer import Developer
from app.models.developer_session import DeveloperSession

def get_developer_from_session(
    request: Request,
    db: Session = Depends(get_db)
) -> tuple[Developer, DeveloperSession]:

    token = request.cookies.get("dev_session_token")

    if token is None:
        raise HTTPException(status_code = 401, detail = "Not authenticated")

    session = (
        db.query(DeveloperSession)
        .filter(DeveloperSession.token == token, DeveloperSession.revoked == False)
        .first()
    )

    if session is None or session.expires_at <= utcnow_naive():
        raise HTTPException(status_code = 401, detail = "Not authenticated")

    developer = db.query(Developer).filter(Developer.id == session.developer_id).first()

    if developer is None:
        raise HTTPException(status_code = 401, detail = "Not authenticated")

    session.expires_at = utcnow_naive() + settings.session_lifetime
    db.commit()

    return developer, session
