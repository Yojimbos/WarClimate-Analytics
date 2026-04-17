from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class DailyJoinedRecord(BaseModel):
    date: date
    personnel_losses: int
    avg_temperature_c: float | None
    precipitation_mm: float | None
    weather_summary: str | None
    rolling_losses_7d: float | None
    rolling_temp_7d: float | None


class SummaryCard(BaseModel):
    label: str
    value: str
    context: str | None = None


class CorrelationResponse(BaseModel):
    from_date: date
    to_date: date
    location: str
    pearson_temperature_vs_losses: float | None
    spearman_temperature_vs_losses: float | None
    pearson_precipitation_vs_losses: float | None
    spearman_precipitation_vs_losses: float | None
    records: list[DailyJoinedRecord]
    insights: list[str]


class SummaryResponse(BaseModel):
    from_date: date
    to_date: date
    location: str
    cards: list[SummaryCard]
    sources: list[dict[str, str]]
    limitations: list[str]
