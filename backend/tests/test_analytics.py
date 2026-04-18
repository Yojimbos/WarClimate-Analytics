from __future__ import annotations

from datetime import date, datetime, timezone

from app.models.losses_daily import LossesDaily
from app.models.weather_daily import WeatherDaily
from app.services.analytics.service import AnalyticsService


def test_correlation_payload_has_records(db_session) -> None:
    db_session.add(
        LossesDaily(
            date=date(2026, 4, 11),
            personnel_losses=1300,
            source_name="Ministry of Defence of Ukraine",
            source_url="https://mod.gov.ua/example-2",
            fetched_at=datetime.now(timezone.utc),
        )
    )
    db_session.add(
        WeatherDaily(
            date=date(2026, 4, 11),
            location_name="Kharkiv",
            avg_temperature_c=14.0,
            min_temperature_c=9.0,
            max_temperature_c=17.5,
            precipitation_mm=0.0,
            wind_speed_km_h=20.0,
            humidity_percent=58.0,
            pressure_hpa=1012.0,
            weather_code="1",
            weather_summary="Mainly clear",
            source_name="Open-Meteo Archive API",
            source_url="https://open-meteo.test",
            fetched_at=datetime.now(timezone.utc),
        )
    )
    db_session.commit()
    payload = AnalyticsService(db_session).get_correlation_payload(
        date(2026, 4, 4), date(2026, 4, 11), "kharkiv"
    )
    assert len(payload["records"]) == 2
    assert payload["pearson_temperature_vs_losses"] is not None
