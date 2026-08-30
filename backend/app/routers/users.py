from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.models.user import User
from app.models.application import Application
from app.models.app_connection import AppConnection
from app.schemas.user import UserResponse

router = APIRouter(prefix = "/applications/{application_id}/users", tags=["users"])

@router.get("/", response_model = list[UserResponse])
def list_users(application_id: int, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code = 404, detail = "Application not found")

    return (
        db.query(User)
        .join(AppConnection, AppConnection.user_id == User.id)
        .filter(AppConnection.application_id == application_id)
        .all()
    )
