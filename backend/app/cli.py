from __future__ import annotations

import argparse
import asyncio
import json
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy import select

from app.core.validation import range_from_days
from app.db.bootstrap import upgrade_database
from app.db.session import SessionLocal
from app.models.losses_daily import LossesDaily
from app.models.weather_daily import WeatherDaily
from app.services.constants import LOCATIONS, LOSSES_SOURCE_NAME, WEATHER_SOURCE_NAME
from app.services.ingestion.service import IngestionService


def seed_sample_data() -> None:
    upgrade_database()
    db = SessionLocal()
    try:
        losses_payload = json.loads(
            Path("sample_data/losses_sample.json").read_text(encoding="utf-8")
        )
        weather_payload = json.loads(
            Path("sample_data/weather_sample.json").read_text(encoding="utf-8")
        )
        for item in losses_payload:
            existing = db.execute(
                select(LossesDaily).where(LossesDaily.date == date.fromisoformat(item["date"]))
            ).scalar_one_or_none()
            if existing is None:
                db.add(
                    LossesDaily(
                        date=date.fromisoformat(item["date"]),
                        personnel_losses=item["personnel_losses"],
                        source_name=LOSSES_SOURCE_NAME,
                        source_url=item["source_url"],
                        fetched_at=datetime.now(timezone.utc),
                        raw_payload=item,
                        raw_text=item.get("raw_text"),
                    )
                )
        for _location_key, location_data in LOCATIONS.items():
            for item in weather_payload:
                existing = db.execute(
                    select(WeatherDaily).where(
                        WeatherDaily.date == date.fromisoformat(item["date"]),
                        WeatherDaily.location_name == location_data["name"],
                    )
                ).scalar_one_or_none()
                if existing is None:
                    db.add(
                        WeatherDaily(
                            date=date.fromisoformat(item["date"]),
                            location_name=location_data["name"],
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
                            fetched_at=datetime.now(timezone.utc),
                        )
                    )
        db.commit()
    finally:
        db.close()


async def run_ingest(days: int, location: str) -> None:
    from_date, to_date = range_from_days(days)
    upgrade_database()
    db = SessionLocal()
    try:
        service = IngestionService(db)
        await service.ingest_losses(from_date, to_date)
        await service.ingest_weather(from_date, to_date, location)
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed_parser = subparsers.add_parser("seed")
    seed_parser.add_argument("--with-sample-data", action="store_true")

    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument("--days", type=int, default=30)
    ingest_parser.add_argument("--location", type=str, default="kharkiv")

    args = parser.parse_args()
    if args.command == "seed" and args.with_sample_data:
        seed_sample_data()
    elif args.command == "ingest":
        asyncio.run(run_ingest(args.days, args.location))


if __name__ == "__main__":
    main()
