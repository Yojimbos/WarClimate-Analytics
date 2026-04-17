from __future__ import annotations

import logging
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.data_source import DataSource
from app.models.ingestion_run import IngestionRun
from app.models.losses_daily import LossesDaily
from app.models.weather_daily import WeatherDaily
from app.services.adapters.factory import get_losses_adapter, get_weather_adapter
from app.services.constants import get_location

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _start_run(self, job_name: str, source_name: str) -> IngestionRun:
        run = IngestionRun(job_name=job_name, source_name=source_name, status="running")
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def _finish_run(
        self, run: IngestionRun, status: str, details: dict | None = None, error: str | None = None
    ) -> None:
        run.status = status
        run.finished_at = datetime.now(timezone.utc)
        run.details = details
        run.error_message = error
        self.db.add(run)
        self.db.commit()

    def _ensure_source(self, name: str, kind: str, base_url: str, description: str) -> None:
        existing = self.db.execute(
            select(DataSource).where(DataSource.name == name)
        ).scalar_one_or_none()
        if existing:
            return
        self.db.add(DataSource(name=name, kind=kind, base_url=base_url, description=description))
        self.db.commit()

    async def ingest_losses(self, from_date: date, to_date: date) -> int:
        adapter = get_losses_adapter()
        run = self._start_run("losses_ingestion", adapter.name)
        imported = 0
        try:
            records = await adapter.fetch_range(from_date, to_date)
            for record in records:
                existing = self.db.execute(
                    select(LossesDaily).where(LossesDaily.date == record.date)
                ).scalar_one_or_none()
                if existing is None:
                    existing = LossesDaily(
                        date=record.date,
                        personnel_losses=record.personnel_losses,
                        source_name=record.source_name,
                        source_url=record.source_url,
                    )
                existing.personnel_losses = record.personnel_losses
                existing.source_name = record.source_name
                existing.source_url = record.source_url
                existing.raw_payload = record.raw_payload
                existing.raw_text = record.raw_text
                existing.fetched_at = datetime.now(timezone.utc)
                self.db.add(existing)
                imported += 1
            self.db.commit()
            self._finish_run(run, "success", {"imported": imported})
            return imported
        except Exception as exc:
            self.db.rollback()
            logger.exception("losses_ingestion_failed")
            self._finish_run(run, "failed", error=str(exc))
            raise

    async def ingest_weather(self, from_date: date, to_date: date, location: str) -> int:
        location_key = location.lower()
        get_location(location_key)
        adapter = get_weather_adapter()
        run = self._start_run("weather_ingestion", adapter.name)
        imported = 0
        try:
            records = await adapter.fetch_range(from_date, to_date, location_key)
            for record in records:
                existing = self.db.execute(
                    select(WeatherDaily).where(
                        WeatherDaily.date == record.date,
                        WeatherDaily.location_name == record.location_name,
                    )
                ).scalar_one_or_none()
                if existing is None:
                    existing = WeatherDaily(
                        date=record.date,
                        location_name=record.location_name,
                        source_name=record.source_name,
                        source_url=record.source_url,
                    )
                existing.avg_temperature_c = record.avg_temperature_c
                existing.min_temperature_c = record.min_temperature_c
                existing.max_temperature_c = record.max_temperature_c
                existing.precipitation_mm = record.precipitation_mm
                existing.wind_speed_km_h = record.wind_speed_km_h
                existing.humidity_percent = record.humidity_percent
                existing.pressure_hpa = record.pressure_hpa
                existing.weather_code = record.weather_code
                existing.weather_summary = record.weather_summary
                existing.source_name = record.source_name
                existing.source_url = record.source_url
                existing.fetched_at = datetime.now(timezone.utc)
                self.db.add(existing)
                imported += 1
            self.db.commit()
            self._finish_run(run, "success", {"imported": imported, "location": location_key})
            return imported
        except Exception as exc:
            self.db.rollback()
            logger.exception("weather_ingestion_failed")
            self._finish_run(run, "failed", error=str(exc))
            raise
