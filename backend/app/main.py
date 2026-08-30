from fastapi import FastAPI
from app.core.database import Base, engine
from app.models import application
from app.routers import applications, users, auth, face

Base.metadata.create_all(bind = engine)

app = FastAPI(title = "FaceAuth")

@app.get("/")
def root():
    return {"Message": "FaceAuth backend is running"}

app.include_router(applications.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(face.router)
