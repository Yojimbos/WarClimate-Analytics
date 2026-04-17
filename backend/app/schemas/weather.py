from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class WeatherDailyRead(BaseModel):
    date: date
    location_name: str
    avg_temperature_c: float | None
    min_temperature_c: float | None
    max_temperature_c: float | None
    precipitation_mm: float | None
    wind_speed_km_h: float | None
    humidity_percent: float | None
    pressure_hpa: float | None
    weather_code: str | None
    weather_summary: str | None
    source_name: str
    source_url: str
    fetched_at: datetime


class WeatherListResponse(BaseModel):
    items: list[WeatherDailyRead]
    total: int
