from fastapi import APIRouter, Depends, Response, Form, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import generate_client_id, generate_client_secret, hash_secret, verify_secret
from app.core.dev_session import get_or_create_developer_session, set_developer_session_cookie
from app.core.dev_dependencies import get_developer_from_session
from app.models.developer import Developer
from app.models.application import Application
from app.schemas.developer import DeveloperAuthRequest
from app.schemas.application import ApplicationCreate, UpdateApplicationRequest

router = APIRouter(prefix = "/developer", tags = ["developer"])

@router.post("/register")
def register_developer(
    response: Response,
    body: DeveloperAuthRequest,
    db: Session = Depends(get_db)
):
    existing = db.query(Developer).filter(Developer.email == body.email).first()
    if existing:
        raise HTTPException(status_code = 400, detail = "Email already registered")

    developer = Developer(
        email = body.email,
        password_hash = hash_secret(body.password),
        created_at = datetime.now(timezone.utc),
    )

    db.add(developer)
    db.commit()
    db.refresh(developer)

    session = get_or_create_developer_session(developer.id, db)
    set_developer_session_cookie(response, session)

    return {"id": developer.id, "email": developer.email}

@router.post("/login")
def login_developer(
    response: Response,
    body: DeveloperAuthRequest,
    db: Session = Depends(get_db)
):
    developer = db.query(Developer).filter(Developer.email == body.email).first()
    if not developer or not verify_secret(body.password, developer.password_hash):
        raise HTTPException(status_code = 401, detail = "Invalid email or password")

    session = get_or_create_developer_session(developer.id, db)
    set_developer_session_cookie(response, session)

    return {"id": developer.id, "email": developer.email}

@router.get("/me")
def get_developer_me(
    developer_and_session: tuple[Developer, DeveloperSession] = Depends(get_developer_from_session)
):
    developer, _ = developer_and_session
    
    return {"id": developer.id, "email": developer.email}


@router.post("/logout")
def logout_developer(
    response: Response,
    developer_and_session: tuple[Developer, DeveloperSession] = Depends(get_developer_from_session),
    db: Session = Depends(get_db)
):
    _, session = developer_and_session

    db.delete(session)
    db.commit()
    
    response.delete_cookie("dev_session_token")
    
    return {"detail": "Logged out"}

@router.post("/applications")
def create_application(
    body: ApplicationCreate,
    developer_and_session: tuple[Developer, DeveloperSession] = Depends(get_developer_from_session),
    db: Session = Depends(get_db)
):
    developer, _ = developer_and_session

    client_id = generate_client_id()
    client_secret = generate_client_secret()

    application = Application(
        developer_id = developer.id,
        name = body.name,
        client_id = client_id,
        client_secret_hash = hash_secret(client_secret),
        redirect_url = body.redirect_url
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "id": application.id,
        "name": application.name,
        "client_id": application.client_id,
        "client_secret": client_secret,
        "redirect_url": application.redirect_url
    }

@router.get("/applications")
def list_applications(
    developer_and_session: tuple[Developer, DeveloperSession] = Depends(get_developer_from_session),
    db: Session = Depends(get_db)
):
    developer, _ = developer_and_session

    applications = db.query(Application).filter(Application.developer_id == developer.id).all()

    return [
        {
            "id": app.id,
            "name": app.name,
            "client_id": app.client_id,
            "redirect_url": app.redirect_url
        }
        for app in applications
    ]

@router.delete("/applications/{application_id}")
def delete_application(
    application_id: int,
    developer_and_session: tuple[Developer, DeveloperSession] = Depends(get_developer_from_session),
    db: Session = Depends(get_db)
):
    developer, _ = developer_and_session

    application = (
        db.query(Application)
        .filter(Application.id == application_id, Application.developer_id == developer.id)
        .first()
    )

    if application is None:
        raise HTTPException(status_code = 404, detail = "Application not found")

    db.delete(application)
    db.commit()

    return {"detail": "Application deleted"}

@router.patch("/applications/{application_id}")
def update_application(
    application_id: int,
    body: UpdateApplicationRequest,
    developer_and_session: tuple[Developer, DeveloperSession] = Depends(get_developer_from_session),
    db: Session = Depends(get_db)
):
    developer, _ = developer_and_session

    application = (
        db.query(Application)
        .filter(Application.id == application_id, Application.developer_id == developer.id)
        .first()
    )

    if application is None:
        raise HTTPException(status_code = 404, detail = "Application not found")

    if body.name is not None:
        application.name = body.name

    if body.redirect_url is not None:
        application.redirect_url = body.redirect_url

    db.commit()
    db.refresh(application)

    return {
        "id": application.id,
        "name": application.name,
        "client_id": application.client_id,
        "redirect_url": application.redirect_url,
    }
