from datetime import datetime

from pydantic import BaseModel, HttpUrl


class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_code: str | None = None


class ShortenResponse(BaseModel):
    code: str
    short_url: str
    original_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StatsResponse(BaseModel):
    code: str
    original_url: str
    created_at: datetime
    hit_count: int

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    environment: str
