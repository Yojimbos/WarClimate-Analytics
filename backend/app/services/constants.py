from __future__ import annotations

LOCATIONS = {
    "kharkiv": {"name": "Kharkiv", "latitude": 49.9935, "longitude": 36.2304},
    "dnipro": {"name": "Dnipro", "latitude": 48.4647, "longitude": 35.0462},
    "zaporizhzhia": {"name": "Zaporizhzhia", "latitude": 47.8388, "longitude": 35.1396},
}

LOSSES_SOURCE_NAME = "Ministry of Defence of Ukraine"
LOSSES_SOURCE_BASE_URL = "https://mod.gov.ua/en/news"
WEATHER_SOURCE_NAME = "Open-Meteo Archive API"
WEATHER_SOURCE_BASE_URL = "https://archive-api.open-meteo.com/v1/archive"


def get_location(location: str) -> dict:
    location_key = location.lower()
    if location_key not in LOCATIONS:
        raise ValueError(
            f"Unsupported location '{location}'. Choose one of: {', '.join(sorted(LOCATIONS))}."
        )
    return LOCATIONS[location_key]
