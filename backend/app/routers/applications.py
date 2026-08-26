from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import generate_client_id, generate_client_secret, hash_secret
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationCreateResponse

router = APIRouter()

@router.post("/applications", response_model = ApplicationCreateResponse)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    raw_secret = generate_client_secret()

    db_app = Application(
        name = payload.name,
        client_id = generate_client_id(),
        client_secret_hash = hash_secret(raw_secret),
        redirect_url = payload.redirect_url
    )

    db.add(db_app)
    db.commit()
    db.refresh(db_app)

    return ApplicationCreateResponse(
        id = db_app.id,
        name = db_app.name,
        client_id = db_app.client_id,
        redirect_url = db_app.redirect_url,
        created_at = db_app.created_at,
        client_secret = raw_secret
    )
