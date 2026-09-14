from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.routers import applications, users, auth, face, admin, developer

Base.metadata.create_all(bind = engine)

app = FastAPI(title = "FaceAuth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"Message": "FaceAuth backend is running"}

app.include_router(applications.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(face.router)
app.include_router(admin.router)
app.include_router(developer.router)
