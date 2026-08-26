from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.models.user import User
from app.models.application import Application
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix = "/applications/{application_id}/users", tags=["users"])

@router.post("/", response_model = UserResponse, status_code = 201)
def create_user(application_id: int, user_in: UserCreate, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code = 404, detail = "Application not found")

    db_user = User(application_id = application_id, username = user_in.username)
    db.add(db_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code = 409, detail = "Username already exists")

    db.refresh(db_user)
    return db_user

@router.get("/", response_model = list[UserResponse])
def list_users(application_id: int, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code = 404, detail = "Application not found")

    return db.query(User).filter(User.application_id == application_id).all()

