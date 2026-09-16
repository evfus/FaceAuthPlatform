import httpx
from fastapi import FastAPI, HTTPException, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
FACEAUTH_URL = os.environ.get("FACEAUTH_URL", "http://localhost:8000")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "myapp-backend"}

@app.get("/callback")
def callback(code: str):
    response = httpx.post( f"{FACEAUTH_URL}/auth/token",
        json={
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
    )

    response.raise_for_status()
    token_data = response.json()

    redirect = RedirectResponse(url="http://localhost:5174/")

    redirect.set_cookie(
        key = "myapp_session",
        value = token_data["token"],
        httponly = True
    )

    return redirect

@app.get("/me")
def me(myapp_session: str | None = Cookie(default=None)):
    if myapp_session is None:
        raise HTTPException(status_code=401, detail="Not logged in")

    response = httpx.get(
        f"{FACEAUTH_URL}/auth/userinfo",
        headers={"Authorization": f"Bearer {myapp_session}"}
    )

    response.raise_for_status()
    return response.json()

