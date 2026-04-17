from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class ReimportRequest(BaseModel):
    days: int = Field(default=30, ge=7, le=365)
    location: str = Field(default="kyiv", min_length=2, max_length=40)
    from_date: date | None = None
    to_date: date | None = None


class ReimportResponse(BaseModel):
    status: str
    losses_imported: int
    weather_imported: int
