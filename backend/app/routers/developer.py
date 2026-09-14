from fastapi import APIRouter, Depends, Response, Form, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import hash_secret, verify_secret
from app.core.dev_session import get_or_create_developer_session, set_developer_session_cookie
from app.core.dev_dependencies import get_developer_from_session
from app.models.developer import Developer

router = APIRouter(prefix = "/developer", tags = ["developer"])

@router.post("/register")
def register_developer(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    existing = db.query(Developer).filter(Developer.email == email).first()
    if existing:
        raise HTTPException(status_code = 400, detail = "Email already registered")

    developer = Developer(
        email = email,
        password_hash = hash_secret(password),
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
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    developer = db.query(Developer).filter(Developer.email == email).first()
    if not developer or not verify_secret(password, developer.password_hash):
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
    db: Session = Depends(get_db),
):
    _, session = developer_and_session

    db.delete(session)
    db.commit()
    
    response.delete_cookie("dev_session_token")
    
    return {"detail": "Logged out"}
