from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.core.database import get_db
from app.core.security import generate_auth_code
from app.models.application import Application
from app.models.user import User
from app.models.auth_code import AuthCode

router = APIRouter(prefix = "/auth", tags = ["auth"])

@router.get("/authorize")
def authorize(client_id: str = Query(...), redirect_url: str = Query(...), user_id: int = Query(...), db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.client_id == client_id).first()

    if not application:
        raise HTTPException(status_code = 400, detail = "Invalid client_id")

    if application.redirect_url != redirect_url:
        raise HTTPException(status_code = 400, detail = "redirect_url does not match registered value")

    user = db.query(User).filter(User.id == user_id and User.application_id == application.id).first()

    if not user:
        raise HTTPException(status_code = 400, detail = "Invalid user_id")

    code = generate_auth_code()
    auth_code = AuthCode(
        code = code,
        user_id = user_id,
        application_id = application.id,
        expires_at = datetime.now(timezone.utc) + timedelta(minutes = 5)
    )

    db.add(auth_code)
    db.commit()

    return RedirectResponse(url = f"{redirect_url}?code={code}")
