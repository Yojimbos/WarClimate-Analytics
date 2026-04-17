from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class LossesRecordPayload:
    date: date
    personnel_losses: int
    source_name: str
    source_url: str
    raw_payload: dict | None = None
    raw_text: str | None = None


@dataclass(slots=True)
class WeatherRecordPayload:
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


class LossesAdapter:
    name: str

    async def fetch_range(self, from_date: date, to_date: date) -> list[LossesRecordPayload]:
        raise NotImplementedError


class WeatherAdapter:
    name: str

    async def fetch_range(
        self, from_date: date, to_date: date, location: str
    ) -> list[WeatherRecordPayload]:
        raise NotImplementedError
