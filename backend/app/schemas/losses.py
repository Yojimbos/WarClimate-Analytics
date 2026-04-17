from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class LossesDailyRead(BaseModel):
    date: date
    personnel_losses: int
    source_name: str
    source_url: str
    fetched_at: datetime


class LossesListResponse(BaseModel):
    items: list[LossesDailyRead]
    total: int
