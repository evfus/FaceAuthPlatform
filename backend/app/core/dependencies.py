from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.core.database import get_db
from app.core.security import utcnow_naive
from app.models.user import User
from app.models.user_session import UserSession

def get_user_from_session(
    request: Request,
    db: Session = Depends(get_db)
) -> tuple[User, UserSession]:

    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code = 401, detail = "Not authenticated")

    session = db.query(UserSession).filter(UserSession.token == session_token).first()

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
