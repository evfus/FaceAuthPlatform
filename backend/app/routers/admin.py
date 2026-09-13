from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.authentication_event import AuthenticationEvent
from app.models.user import User
from app.models.application import Application

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/auth-events")
def get_auth_events(db: Session = Depends(get_db)):
    events = (
        db.query(AuthenticationEvent, User, Application)
        .outerjoin(User, AuthenticationEvent.user_id == User.id)
        .outerjoin(Application, AuthenticationEvent.application_id == Application.id)
        .order_by(AuthenticationEvent.created_at.desc())
        .all()
    )

    return [
        {
            "id": event.id,
            "created_at": event.created_at,
            "result": event.result,
            "confidence": event.confidence,
            "reason": event.reason,
            "user_email": user.email if user else None,
            "application_name": application.name if application else None,
        }
        for event, user, application in events
    ]
