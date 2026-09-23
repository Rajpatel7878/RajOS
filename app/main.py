"""RajOS FastAPI Application Entry Point.

Initialises the FastAPI app, registers middleware, creates DB tables on
startup, and includes all feature routers.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.database.connection import Base, engine

# Initialise structured logging first
setup_logging()
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# FastAPI Application
# ------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ------------------------------------------------------------------
# CORS Middleware — origins driven by environment variable
# ------------------------------------------------------------------
cors_origins = settings.get_cors_origins()
logger.info("CORS allowed origins: %s", cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Import ALL models before create_all so SQLAlchemy sees them
# ------------------------------------------------------------------
from app.models.user import User  # noqa: F401, E402
from app.models.task import Task  # noqa: F401, E402
from app.models.note import Note  # noqa: F401, E402
from app.models.memory import Memory  # noqa: F401, E402
from app.models.document import Document  # noqa: F401, E402
from app.models.conversation import Conversation  # noqa: F401, E402
from app.models.message import Message  # noqa: F401, E402
from app.models.preference import UserPreference  # noqa: F401, E402
from app.automation.automation_models import Automation  # noqa: F401, E402

# Create tables for any new models (existing data is preserved)
Base.metadata.create_all(bind=engine)
logger.info("Database tables verified/created.")

# ------------------------------------------------------------------
# Routers — authentication & users
# ------------------------------------------------------------------
from app.routes.auth import router as auth_router  # noqa: E402
from app.routes.user import router as user_router  # noqa: E402

app.include_router(auth_router)
app.include_router(user_router)

# ------------------------------------------------------------------
# Routers — core features
# ------------------------------------------------------------------
from app.routers import tasks, notes, memory, assistant, chat, documents, productivity, dashboard, tools  # noqa: E402

app.include_router(tasks.router)
app.include_router(notes.router)
app.include_router(memory.router)
app.include_router(assistant.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(productivity.router)
app.include_router(dashboard.router)
app.include_router(tools.router)

# ------------------------------------------------------------------
# Routers — advanced features
# ------------------------------------------------------------------
from app.search.search_router import router as search_router  # noqa: E402
from app.automation import automation_router  # noqa: E402
from app.embeddings.embedding_router import router as embedding_router  # noqa: E402
from app.vector_db.vector_router import router as vector_router  # noqa: E402
from app.rag.rag_router import router as rag_router  # noqa: E402
from app.llm.llm_router_api import router as llm_router  # noqa: E402

app.include_router(search_router)
app.include_router(automation_router.router)
app.include_router(embedding_router)
app.include_router(vector_router)
app.include_router(rag_router)
app.include_router(llm_router)


# ------------------------------------------------------------------
# Built-in utility endpoints
# ------------------------------------------------------------------
@app.get("/", tags=["Status"])
def root():
    """Application root — basic identification response."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Status"])
def health():
    """Health check — always returns healthy if the process is running."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
    }


@app.get("/readiness", tags=["Status"])
def readiness():
    """Readiness check — verifies the database can be reached."""
    from sqlalchemy import text
    from app.database.connection import SessionLocal

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "ok"
    except Exception as exc:
        logger.error("Readiness DB check failed: %s", exc)
        db_status = "error"

    llm_configured = bool(settings.GEMINI_API_KEY or settings.OPENAI_API_KEY)

    return {
        "status": "ready" if db_status == "ok" else "degraded",
        "database": db_status,
        "llm_configured": llm_configured,
        "default_provider": settings.DEFAULT_LLM_PROVIDER,
    }
