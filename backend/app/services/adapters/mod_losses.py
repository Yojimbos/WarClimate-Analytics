from __future__ import annotations

import logging
import re
from datetime import date, timedelta

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed

from app.services.adapters.base import LossesAdapter, LossesRecordPayload
from app.services.constants import LOSSES_SOURCE_BASE_URL, LOSSES_SOURCE_NAME

logger = logging.getLogger(__name__)
PERSONNEL_PATTERN = re.compile(r"personnel\s*[-:]\s*about\s*([\d,]+)", re.IGNORECASE)


class ModOfficialLossesAdapter(LossesAdapter):
    name = "mod_official"

    @staticmethod
    def _article_url(target_date: date) -> str:
        month = target_date.strftime("%B").lower()
        return f"{LOSSES_SOURCE_BASE_URL}/total-russian-combat-losses-in-ukraine-as-of-{month}-{target_date.day}-{target_date.year}"

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def _fetch_article(self, client: httpx.AsyncClient, url: str) -> str:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

    @staticmethod
    def _parse_personnel_losses(html: str) -> tuple[int, str]:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)
        match = PERSONNEL_PATTERN.search(text)
        if not match:
            raise ValueError("Could not parse personnel losses from official page.")
        return int(match.group(1).replace(",", "")), text

    async def fetch_range(self, from_date: date, to_date: date) -> list[LossesRecordPayload]:
        cumulative_by_date: dict[date, tuple[int, str, str]] = {}
        async with httpx.AsyncClient(
            timeout=15.0, headers={"User-Agent": "enemy-losses-weather-demo/0.1"}
        ) as client:
            current = from_date - timedelta(days=1)
            while current <= to_date:
                url = self._article_url(current)
                try:
                    html = await self._fetch_article(client, url)
                    cumulative_total, raw_text = self._parse_personnel_losses(html)
                    cumulative_by_date[current] = (cumulative_total, url, raw_text)
                except Exception as exc:
                    logger.warning(
                        "losses_adapter_fetch_failed",
                        extra={"date": current.isoformat(), "url": url, "error": str(exc)},
                    )
                current += timedelta(days=1)
        records: list[LossesRecordPayload] = []
        current = from_date
        while current <= to_date:
            previous = current - timedelta(days=1)
            if current in cumulative_by_date and previous in cumulative_by_date:
                current_total, url, raw_text = cumulative_by_date[current]
                previous_total, _, _ = cumulative_by_date[previous]
                daily_losses = max(current_total - previous_total, 0)
                records.append(
                    LossesRecordPayload(
                        date=current,
                        personnel_losses=daily_losses,
                        source_name=LOSSES_SOURCE_NAME,
                        source_url=url,
                        raw_payload={
                            "cumulative_total": current_total,
                            "previous_cumulative_total": previous_total,
                            "derived_daily_delta": daily_losses,
                        },
                        raw_text=raw_text[:5000],
                    )
                )
            current += timedelta(days=1)
        return records
