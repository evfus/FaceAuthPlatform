from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.core.database import get_db
from app.core.security import utcnow_naive
from app.models.user import User
from app.models.user_session import UserSession

session_security = HTTPBearer(scheme_name = "SessionAuth")

def get_user_from_session(
    credentials: HTTPAuthorizationCredentials = Depends(session_security),
    db: Session = Depends(get_db)
) -> tuple[User, UserSession]:

    session = db.query(UserSession).filter(UserSession.token == credentials.credentials).first()

    if not session:
        raise HTTPException(status_code = 401, detail = "Invalid session")
    if session.revoked:
        raise HTTPException(status_code = 401, detail = "Session revoked")
    if session.expires_at < utcnow_naive():
        raise HTTPException(status_code = 401, detail = "Session expired")

    session.expires_at = datetime.now(timezone.utc) + timedelta(hours = 24)
    db.commit()

    user = db.query(User).filter(User.id == session.user_id).first()

    if not user:
        raise HTTPException(status_code = 404, detail = "User not found")

    return user, session
