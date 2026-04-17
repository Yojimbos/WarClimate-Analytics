from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from app.core.config import get_settings
from app.services.adapters.base import WeatherAdapter, WeatherRecordPayload
from app.services.constants import WEATHER_SOURCE_NAME, get_location


class SampleWeatherAdapter(WeatherAdapter):
    name = "sample_weather"

    def __init__(self) -> None:
        self.settings = get_settings()

    async def fetch_range(
        self, from_date: date, to_date: date, location: str
    ) -> list[WeatherRecordPayload]:
        location_name = get_location(location)["name"]
        path = Path(self.settings.data_dir) / "weather_sample.json"
        records = json.loads(path.read_text(encoding="utf-8"))
        return [
            WeatherRecordPayload(
                date=date.fromisoformat(item["date"]),
                location_name=location_name,
                avg_temperature_c=item["avg_temperature_c"],
                min_temperature_c=item["min_temperature_c"],
                max_temperature_c=item["max_temperature_c"],
                precipitation_mm=item["precipitation_mm"],
                wind_speed_km_h=item["wind_speed_km_h"],
                humidity_percent=item["humidity_percent"],
                pressure_hpa=item["pressure_hpa"],
                weather_code=item["weather_code"],
                weather_summary=item["weather_summary"],
                source_name=WEATHER_SOURCE_NAME,
                source_url=item["source_url"],
            )
            for item in records
            if from_date <= date.fromisoformat(item["date"]) <= to_date
        ]
