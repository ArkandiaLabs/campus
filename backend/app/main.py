from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import close_pool, create_pool, set_pool
from app.infrastructure.routers import catalog, health, progress


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    pool = await create_pool(settings.database_url)
    set_pool(pool)
    yield
    await close_pool(pool)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Arkandia Campus API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api/v1")
    app.include_router(catalog.router, prefix="/api/v1")
    app.include_router(progress.router, prefix="/api/v1")

    return app


app = create_app()
