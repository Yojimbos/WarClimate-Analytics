from __future__ import annotations

from collections.abc import Generator
from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.losses_daily import LossesDaily
from app.models.weather_daily import WeatherDaily

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(
        LossesDaily(
            date=date(2026, 4, 10),
            personnel_losses=1230,
            source_name="Ministry of Defence of Ukraine",
            source_url="https://mod.gov.ua/example",
            fetched_at=datetime.now(timezone.utc),
        )
    )
    db.add(
        WeatherDaily(
            date=date(2026, 4, 10),
            location_name="Kyiv",
            avg_temperature_c=12.3,
            min_temperature_c=8.0,
            max_temperature_c=15.5,
            precipitation_mm=1.1,
            wind_speed_km_h=18.0,
            humidity_percent=65.0,
            pressure_hpa=1008.0,
            weather_code="2",
            weather_summary="Partly cloudy",
            source_name="Open-Meteo Archive API",
            source_url="https://open-meteo.test",
            fetched_at=datetime.now(timezone.utc),
        )
    )
    db.commit()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
