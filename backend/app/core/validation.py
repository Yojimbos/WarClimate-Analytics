from __future__ import annotations

from datetime import date, timedelta

from fastapi import HTTPException, status

MAX_RANGE_DAYS = 365
MIN_RANGE_DAYS = 7


def validate_date_range(from_date: date, to_date: date) -> None:
    if from_date > to_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid date range."
        )
    span = (to_date - from_date).days + 1
    if span < MIN_RANGE_DAYS or span > MAX_RANGE_DAYS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Date range must be between {MIN_RANGE_DAYS} and {MAX_RANGE_DAYS} days.",
        )


def range_from_days(days: int) -> tuple[date, date]:
    if days < MIN_RANGE_DAYS or days > MAX_RANGE_DAYS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Days out of bounds."
        )
    to_date = date.today()
    from_date = to_date - timedelta(days=days - 1)
    return from_date, to_date
