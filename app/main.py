from fastapi import FastAPI
from app.database.connection import Base, engine
from app.models.user import User
from app.core.config import settings
from app.core.logging import setup_logging

# Initialize logging
setup_logging()

# Create FastAPI application
app = FastAPI(


    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

from app.routes.auth import router as auth_router
app.include_router(auth_router)


Base.metadata.create_all(bind=engine)

# Root endpoint
@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
    }

# Health check endpoint
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "debug": settings.DEBUG,
    }

from app.routes.user import router as user_router
app.include_router(user_router)
from app.models import task
from app.routers import tasks
app.include_router(tasks.router)
from app.routers import notes
app.include_router(notes.router)
from app.routers import memory
app.include_router(memory.router)
from app.routers import assistant
app.include_router(assistant.router)
from app.routers import chat
app.include_router(chat.router)
from app.routers import documents
app.include_router(documents.router)
