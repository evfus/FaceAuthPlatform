from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.core.database import get_db
from app.core.security import generate_auth_code, hash_secret, verify_secret, generate_token, utcnow_naive
from app.schemas.token import TokenRequest, TokenResponse, AuthorizeRequest, AuthResult
from app.schemas.user import UserRegister, UserResponse
from app.models.token import Token
from app.models.application import Application
from app.models.user import User
from app.models.auth_code import AuthCode
from app.services.auth_flow import complete_login_or_signup

router = APIRouter(prefix = "/auth", tags = ["auth"])

security = HTTPBearer(scheme_name = "TokenAuth")

@router.post("/register", response_model = AuthResult, status_code = 201)
def register(
    client_id: str = Query(...),
    redirect_url: str = Query(...),
    user_in: UserRegister = Body(...),
    db: Session = Depends(get_db)
):
    application = db.query(Application).filter(Application.client_id == client_id).first()

    if not application:
        raise HTTPException(status_code = 400, detail = "Invalid client_id")
    if application.redirect_url != redirect_url:
        raise HTTPException(status_code = 400, detail = "redirect_url does not match registered value")

    existing = db.query(User).filter(User.email == user_in.email).first()

    if existing:
        raise HTTPException(status_code = 409, detail = "User already exists with this email address")

    user = User(
        email = user_in.email,
        password_hash = hash_secret(user_in.password)
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)

    return complete_login_or_signup(user, application, db)

@router.post("/authorize", response_model = AuthResult)
def authorize(
    client_id: str = Query(...),
    redirect_url: str = Query(...),
    credentials: AuthorizeRequest = Body(...),
    db: Session = Depends(get_db)
):
    application = db.query(Application).filter(Application.client_id == client_id).first()

    if not application:
        raise HTTPException(status_code = 400, detail = "Invalid client_id")

    if application.redirect_url != redirect_url:
        raise HTTPException(status_code = 400, detail = "redirect_url does not match registered value")

    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_secret(credentials.password, user.password_hash):
        raise HTTPException(status_code = 401, detail = "Invalid email or password")

    return complete_login_or_signup(user, application, db)

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
