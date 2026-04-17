from __future__ import annotations

from datetime import date

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

from app.services.adapters.base import WeatherAdapter, WeatherRecordPayload
from app.services.constants import WEATHER_SOURCE_BASE_URL, WEATHER_SOURCE_NAME, get_location

WEATHER_CODE_MAP = {
    0: "Clear",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    51: "Light drizzle",
    61: "Light rain",
    63: "Rain",
    71: "Snow",
    80: "Rain showers",
    95: "Thunderstorm",
}


class OpenMeteoWeatherAdapter(WeatherAdapter):
    name = "open_meteo_archive"

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def fetch_range(
        self, from_date: date, to_date: date, location: str
    ) -> list[WeatherRecordPayload]:
        loc = get_location(location)
        params = {
            "latitude": loc["latitude"],
            "longitude": loc["longitude"],
            "start_date": from_date.isoformat(),
            "end_date": to_date.isoformat(),
            "daily": ",".join(
                [
                    "temperature_2m_mean",
                    "temperature_2m_min",
                    "temperature_2m_max",
                    "precipitation_sum",
                    "wind_speed_10m_max",
                    "relative_humidity_2m_mean",
                    "surface_pressure_mean",
                    "weather_code",
                ]
            ),
            "timezone": "Europe/Kyiv",
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(WEATHER_SOURCE_BASE_URL, params=params)
            response.raise_for_status()
            payload = response.json()
        daily = payload["daily"]
        records: list[WeatherRecordPayload] = []
        for idx, item_date in enumerate(daily["time"]):
            weather_code = daily["weather_code"][idx]
            records.append(
                WeatherRecordPayload(
                    date=date.fromisoformat(item_date),
                    location_name=loc["name"],
                    avg_temperature_c=daily["temperature_2m_mean"][idx],
                    min_temperature_c=daily["temperature_2m_min"][idx],
                    max_temperature_c=daily["temperature_2m_max"][idx],
                    precipitation_mm=daily["precipitation_sum"][idx],
                    wind_speed_km_h=daily["wind_speed_10m_max"][idx],
                    humidity_percent=daily["relative_humidity_2m_mean"][idx],
                    pressure_hpa=daily["surface_pressure_mean"][idx],
                    weather_code=str(weather_code),
                    weather_summary=WEATHER_CODE_MAP.get(weather_code, "Unknown"),
                    source_name=WEATHER_SOURCE_NAME,
                    source_url=str(response.url),
                )
            )
        return records
