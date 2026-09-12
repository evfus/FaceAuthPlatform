import cv2
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Form, Response, Request, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.core.database import get_db
from app.core.security import generate_auth_code, hash_secret, verify_secret, generate_token, utcnow_naive
from app.schemas.token import TokenRequest, TokenResponse, AuthorizeRequest, AuthResult
from app.schemas.user import UserRegister, UserResponse
from app.schemas.face_login import FaceLoginResponse
from app.models.token import Token
from app.models.application import Application
from app.models.user import User
from app.models.auth_code import AuthCode
from app.models.user_session import UserSession
from app.models.authentication_event import AuthenticationEvent
from app.models.face_embedding import FaceEmbedding
from app.services.auth_flow import complete_login_or_signup
from app.services.face_matching import match_face_to_user
from app.core.face_models import detector, embedder

router = APIRouter(prefix = "/auth", tags = ["auth"])

security = HTTPBearer(scheme_name = "TokenAuth")

@router.get("/email-exists")
def email_exists(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    return {"exists": user is not None}

@router.get("/session-check")
def session_check(
    request: Request,
    client_id: str = Query(...),
    redirect_url: str = Query(...),
    db: Session = Depends(get_db)
):

    application = db.query(Application).filter(Application.client_id == client_id).first()

    if not application:
        raise HTTPException(status_code = 400, detail = "Invalid client_id")

    if application.redirect_url != redirect_url:
        raise HTTPException(status_code = 400, detail = "Invalid redirect_url")

    token = request.cookies.get("session_token")

    if not token:
        return {"logged_in": False}

    session = db.query(UserSession).filter(UserSession.token == token).first()

    if not session or session.revoked or session.expires_at < utcnow_naive():
        return {"logged_in": False}

    user = db.query(User).filter(User.id == session.user_id).first()
    has_face = db.query(FaceEmbedding).filter(FaceEmbedding.user_id == user.id).first()

    if has_face is None:
        session.pending_client_id = client_id
        db.commit()

    return {"logged_in": True, "email": user.email, "needs_enrollment": has_face is None}

@router.post("/register", response_model = AuthResult, status_code = 201)
def register(
    response: Response,
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

    return complete_login_or_signup(user, application, response, db)

@router.post("/authorize", response_model = AuthResult)
def authorize(
    response: Response,
    request: Request,
    client_id: str = Query(...),
    redirect_url: str = Query(...),
    credentials: AuthorizeRequest | None = Body(default = None),
    db: Session = Depends(get_db)
):
    application = db.query(Application).filter(Application.client_id == client_id).first()

    if not application:
        raise HTTPException(status_code = 400, detail = "Invalid client_id")

    if application.redirect_url != redirect_url:
        raise HTTPException(status_code = 400, detail = "redirect_url does not match registered value")

    token = request.cookies.get("session_token")

    if token:
        session = db.query(UserSession).filter(UserSession.token == token).first()

        if session and not session.revoked and session.expires_at > utcnow_naive():
            user = db.query(User).filter(User.id == session.user_id).first()
            return complete_login_or_signup(user, application, response, db)

    if credentials is None:
        raise HTTPException(status_code = 401, detail = "Not logged in and no credentials provided")

    user = db.query(User).filter(User.email == credentials.email).first()
 
    if not user or not verify_secret(credentials.password, user.password_hash):
        if user:
            db.add(AuthenticationEvent(
                application_id = application.id,
                user_id = user.id,
                result = "failure",
                reason = "invalid credentials"
            ))
            db.commit()
            
        raise HTTPException(status_code = 401, detail = "Invalid email or password")

    db.add(AuthenticationEvent(
        application_id = application.id,
        user_id = user.id,
        result = "success",
        reason = None
    ))
    db.commit()

    return complete_login_or_signup(user, application, response, db)

@router.post("/login/face", response_model = FaceLoginResponse)
def login_with_face(
    response: Response,
    email: str = Form(...),
    client_id: str = Form(...),
    redirect_url: str = Form(...),
    file: UploadFile = File(),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code = 404, detail = "No account found for this email")

    application = db.query(Application).filter(Application.client_id == client_id).first()

    if not application:
        raise HTTPException(status_code = 400, detail = "Invalid client_id")

    if application.redirect_url != redirect_url:
        raise HTTPException(status_code = 400, detail = "redirect_url does not match registered value")

    contents = file.file.read()
    frame = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)

    if frame is None:
        raise HTTPException(status_code = 400, detail = "Could not decode uploaded image")

    match_result = match_face_to_user(frame, user, db, detector, embedder)

    event = AuthenticationEvent(
        application_id = application.id,
        user_id = user.id,
        result = "succes" if match_result.matched else "failure",
        confidence = match_result.confidence,
        reason = match_result.reason
    )

    db.add(event)
    db.commit()

    if not match_result.matched:
        return FaceLoginResponse(
            matched = False,
            confidence = match_result.confidence,
            reason = match_result.reason
        )
    
    auth_result = complete_login_or_signup(user, application, response, db)

    return FaceLoginResponse(
        matched = True,
        confidence = match_result.confidence,
        session_token = auth_result.session_token,
        session_expires_at = auth_result.session_expires_at,
        redirect_url = auth_result.redirect_url
    )

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
