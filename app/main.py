from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers import urls


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (migrations handled by Alembic in prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="URL Shortener",
    description="A fast, async URL shortener built with FastAPI and PostgreSQL.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(urls.router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "environment": settings.app_env}
