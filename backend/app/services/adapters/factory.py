from __future__ import annotations

from app.core.config import get_settings
from app.services.adapters.base import LossesAdapter, WeatherAdapter
from app.services.adapters.mod_losses import ModOfficialLossesAdapter
from app.services.adapters.open_meteo_weather import OpenMeteoWeatherAdapter
from app.services.adapters.sample_losses import SampleLossesAdapter
from app.services.adapters.sample_weather import SampleWeatherAdapter


def get_losses_adapter() -> LossesAdapter:
    settings = get_settings()
    if settings.losses_provider == "official":
        return ModOfficialLossesAdapter()
    return SampleLossesAdapter()


def get_weather_adapter() -> WeatherAdapter:
    settings = get_settings()
    if settings.weather_provider == "open-meteo":
        return OpenMeteoWeatherAdapter()
    return SampleWeatherAdapter()
