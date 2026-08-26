from fastapi import FastAPI
from app.core.database import Base, engine
from app.models import application
from app.routers import applications

Base.metadata.create_all(bind = engine)

app = FastAPI(title = "FaceAuth")

app.include_router(applications.router)
