from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

_raw = settings.database_url
if _raw.startswith("sqlite"):
    _url = _raw if "aiosqlite" in _raw else _raw.replace("sqlite://", "sqlite+aiosqlite://")
    engine = create_async_engine(_url, echo=False, connect_args={"check_same_thread": False})
else:
    _url = _raw.replace("postgres://", "postgresql+asyncpg://").replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    engine = create_async_engine(_url, echo=False, pool_pre_ping=True, pool_size=5, max_overflow=10)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
