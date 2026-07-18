import random
import string

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import URL


def _generate_code(length: int) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choices(alphabet, k=length))


async def get_url_by_code(db: AsyncSession, code: str) -> URL | None:
    result = await db.execute(select(URL).where(URL.code == code))
    return result.scalar_one_or_none()


async def get_url_by_original(db: AsyncSession, original_url: str) -> URL | None:
    result = await db.execute(select(URL).where(URL.original_url == original_url))
    return result.scalar_one_or_none()


async def create_short_url(db: AsyncSession, original_url: str, custom_code: str | None = None) -> URL:
    if custom_code:
        code = custom_code
    else:
        # Generate unique code
        for _ in range(10):
            code = _generate_code(settings.code_length)
            existing = await get_url_by_code(db, code)
            if not existing:
                break
        else:
            raise RuntimeError("Failed to generate a unique short code after 10 attempts")

    url = URL(code=code, original_url=original_url)
    db.add(url)
    await db.commit()
    await db.refresh(url)
    return url


async def increment_hit_count(db: AsyncSession, code: str) -> None:
    await db.execute(
        update(URL).where(URL.code == code).values(hit_count=URL.hit_count + 1)
    )
    await db.commit()
