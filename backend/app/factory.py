"""
Application factory: builds and configures the FastAPI app instance.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from config import settings
from database import Base, engine
from routers import auth, habits, logs, dashboard, analytics, profile, achievements

# Import models so they're registered on Base before create_all is called
import models  # noqa: F401


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Production-ready Habit Tracker API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Dev/SQLite convenience: auto-create tables so a fresh clone "just works"
    # with no extra steps. In production, schema is owned by Alembic
    # migrations (run `alembic upgrade head` as a release step) so this is
    # skipped — it would otherwise mask a migration that failed to run.
    if not settings.is_production:
        Base.metadata.create_all(bind=engine)

    # Mount static files if the directory has content (e.g. uploaded avatars)
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
    os.makedirs(static_dir, exist_ok=True)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Routers
    app.include_router(auth.router)
    app.include_router(habits.router)
    app.include_router(logs.router)
    app.include_router(dashboard.router)
    app.include_router(analytics.router)
    app.include_router(profile.router)
    app.include_router(achievements.router)

    @app.get("/", tags=["Health"])
    def health_check():
        return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENV}

    return app
