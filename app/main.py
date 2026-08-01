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


from app.models.preference import UserPreference

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
from app.routers import productivity
app.include_router(productivity.router)
from app.search.search_router import router as search_router
app.include_router(search_router)


from app.automation import automation_router
app.include_router(automation_router.router)

from app.embeddings.embedding_router import router as embedding_router
app.include_router(embedding_router)

from app.vector_db.vector_router import router as vector_router
app.include_router(vector_router)

from app.rag.rag_router import router as rag_router
app.include_router(rag_router)

from app.llm.llm_router_api import router as llm_router
app.include_router(llm_router)
