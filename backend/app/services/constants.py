from __future__ import annotations

LOCATIONS = {
    "kyiv": {"name": "Kyiv", "latitude": 50.4501, "longitude": 30.5234},
    "lviv": {"name": "Lviv", "latitude": 49.8397, "longitude": 24.0297},
    "odesa": {"name": "Odesa", "latitude": 46.4825, "longitude": 30.7233},
    "kharkiv": {"name": "Kharkiv", "latitude": 49.9935, "longitude": 36.2304},
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
