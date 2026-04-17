from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class SourceInfo(BaseModel):
    name: str
    url: str


class DateRangeParams(BaseModel):
    from_date: date
    to_date: date


class HealthResponse(BaseModel):
    status: str
    environment: str
    timestamp: datetime
