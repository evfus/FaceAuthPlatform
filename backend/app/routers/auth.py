from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.core.database import get_db
from app.core.security import generate_auth_code, verify_secret, generate_token, utcnow_naive
from app.schemas.token import TokenRequest, TokenResponse
from app.schemas.user import UserResponse
from app.models.token import Token
from app.models.application import Application
from app.models.user import User
from app.models.auth_code import AuthCode

router = APIRouter(prefix = "/auth", tags = ["auth"])

security = HTTPBearer()

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

@router.post("/token", response_model = TokenResponse)
def exchange_token(request: TokenRequest, db: Session = Depends(get_db)):
    auth_code = db.query(AuthCode).filter(AuthCode.code == request.code).first()

    if not auth_code:
        raise HTTPException(status_code = 400, detail = "Invalid code")

    if auth_code.used:
        raise HTTPException(status_code = 400, detail = "Code already used")

    if auth_code.expires_at < utcnow_naive():
        raise HTTPException(status_code = 400, detail = "Code expired")

    application = db.query(Application).filter(Application.client_id == request.client_id).first()

    if not application:
        raise HTTPException(status_code = 400, detail = "Invalid client_id")

    if not verify_secret(request.client_secret, application.client_secret_hash):
        raise HTTPException(status_code = 400, detail = "Invalid client_secret")

    if auth_code.application_id != application.id:
        raise HTTPException(status_code = 400, detail = "Code does not belong to this application")

    auth_code.used = True
    
    token_value = generate_token()

    token = Token(
        token = token_value,
        user_id = auth_code.user_id,
        application_id = application.id,
        expires_at = datetime.now(timezone.utc) + timedelta(hours = 1)
    )

    db.add(token)
    db.commit()

    return TokenResponse(token = token_value, expires_at = token.expires_at)

@router.get("/users/me", response_model = UserResponse)
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token_value = credentials.credentials

    token = db.query(Token).filter(Token.token == token_value).first()

    if not token:
        raise HTTPException(status_code = 401, detail = "Invalid token")

    if token.expires_at < utcnow_naive():
        raise HTTPException(status_code = 401, detail = "Token expired")

    user = db.query(User).filter(User.id == token.user_id).first()

    if not user:
        raise HTTPException(status_code = 404, detail = "User not found")

    return user
