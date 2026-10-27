from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import get_engine
from app.routes import companion, workspace


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_settings()  # Fail closed before serving if authentication configuration is unsafe.
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Debug Ed API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type", "X-School-ID"],
    )
    app.include_router(workspace.router, prefix="/api/v1")
    app.include_router(companion.router, prefix="/api/v1")

    @app.get("/health/live", tags=["health"])
    def live():
        return {"status": "ok"}

    @app.get("/health/ready", tags=["health"])
    def ready():
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok"}

    return app


app = create_app()
