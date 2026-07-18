from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.config import settings
from app.database import get_db
from app.schemas import ShortenRequest, ShortenResponse, StatsResponse

router = APIRouter()


@router.post("/shorten", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(body: ShortenRequest, db: AsyncSession = Depends(get_db)):
    original_url = str(body.url)

    if body.custom_code:
        existing = await crud.get_url_by_code(db, body.custom_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Code '{body.custom_code}' is already taken.",
            )

    url_obj = await crud.create_short_url(db, original_url, body.custom_code)
    return ShortenResponse(
        code=url_obj.code,
        short_url=f"{settings.base_url}/{url_obj.code}",
        original_url=url_obj.original_url,
        created_at=url_obj.created_at,
    )


@router.get("/stats/{code}", response_model=StatsResponse)
async def get_stats(code: str, db: AsyncSession = Depends(get_db)):
    url_obj = await crud.get_url_by_code(db, code)
    if not url_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short code not found.")
    return StatsResponse(
        code=url_obj.code,
        original_url=url_obj.original_url,
        created_at=url_obj.created_at,
        hit_count=url_obj.hit_count,
    )


@router.get("/{code}")
async def redirect_url(code: str, db: AsyncSession = Depends(get_db)):
    url_obj = await crud.get_url_by_code(db, code)
    if not url_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found.")
    await crud.increment_hit_count(db, code)
    return RedirectResponse(url=url_obj.original_url, status_code=status.HTTP_302_FOUND)
