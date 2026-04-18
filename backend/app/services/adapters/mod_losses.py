from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed

from app.services.adapters.base import LossesAdapter, LossesRecordPayload
from app.services.constants import LOSSES_SOURCE_NAME

logger = logging.getLogger(__name__)

SITEMAP_URL = "https://mod.gov.ua/sitemap.xml"
USER_AGENT = "war-climate-analytics/0.1"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

LOSS_SLUG_HINTS = (
    "combat-losses",
    "losses-in-ukraine-as-of",
    "estimated-combat-losses",
    "losses-of-russians",
)
LOSSES_ON_DATE_PATTERN = re.compile(
    r"(?:losses|military losses)\s+on\s+([A-Z][a-z]+ \d{1,2}, \d{4})\s*:\s*([\d,\s]+)\s+personnel",
    re.IGNORECASE,
)
PERSONNEL_PLUS_PATTERN = re.compile(
    r"(?:Personnel:\s*)?(?:\*?\s*)?(?:approximately|about|personnel:\s*about)\s*([\d\s,]+)\s*\(\+([\d\s,]+)\)\s*persons",
    re.IGNORECASE,
)
PUBLISHED_DATE_PATTERN = re.compile(r"(\d{1,2}\s+[A-Z][a-z]+,\s+\d{4}),\s+\d{1,2}:\d{2}\s+[AP]M")


class ModOfficialLossesAdapter(LossesAdapter):
    name = "mod_official"

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def _fetch_text(self, client: httpx.AsyncClient, url: str) -> str:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

    @staticmethod
    def _extract_urls_from_sitemap(xml_payload: str) -> list[str]:
        root = ET.fromstring(xml_payload)
        urls: list[str] = []
        for loc in root.findall("sm:url/sm:loc", SITEMAP_NS):
            if loc.text:
                urls.append(loc.text.strip())
        return urls

    @classmethod
    def _candidate_article_urls(
        cls, sitemap_urls: list[str], from_date: date, to_date: date
    ) -> list[str]:
        date_tokens = {
            target_date.strftime("%B").lower() + f"-{target_date.day}-{target_date.year}"
            for target_date in _daterange(from_date, to_date)
        }
        candidates: list[str] = []
        for url in sitemap_urls:
            parsed = urlparse(url)
            if parsed.netloc != "mod.gov.ua":
                continue
            if not parsed.path.startswith("/en/news/"):
                continue
            slug = parsed.path.rsplit("/", maxsplit=1)[-1]
            if not any(hint in slug for hint in LOSS_SLUG_HINTS):
                continue
            if not any(token in slug for token in date_tokens):
                continue
            candidates.append(url)
        return sorted(set(candidates))

    @staticmethod
    def _normalize_number(value: str) -> int:
        return int(re.sub(r"[^\d]", "", value))

    @classmethod
    def _parse_personnel_losses(cls, html: str) -> tuple[date, int, int | None, str]:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)

        published_match = PUBLISHED_DATE_PATTERN.search(text)
        if not published_match:
            raise ValueError("Could not parse article publication date from official page.")
        published_date = datetime.strptime(published_match.group(1), "%d %B, %Y").date()

        losses_match = LOSSES_ON_DATE_PATTERN.search(text)
        if losses_match:
            losses_date = datetime.strptime(losses_match.group(1), "%B %d, %Y").date()
            daily_losses = cls._normalize_number(losses_match.group(2))
        else:
            losses_date = published_date - timedelta(days=1)
            daily_losses = None

        personnel_match = PERSONNEL_PLUS_PATTERN.search(text)
        if not personnel_match:
            raise ValueError("Could not parse personnel totals from official page.")

        cumulative_total = cls._normalize_number(personnel_match.group(1))
        if daily_losses is None:
            daily_losses = cls._normalize_number(personnel_match.group(2))

        return losses_date, daily_losses, cumulative_total, text

    async def fetch_range(self, from_date: date, to_date: date) -> list[LossesRecordPayload]:
        article_from = from_date + timedelta(days=1)
        article_to = to_date + timedelta(days=1)
        async with httpx.AsyncClient(
            timeout=20.0, headers={"User-Agent": USER_AGENT}, follow_redirects=True
        ) as client:
            sitemap_xml = await self._fetch_text(client, SITEMAP_URL)
            sitemap_urls = self._extract_urls_from_sitemap(sitemap_xml)
            candidate_urls = self._candidate_article_urls(sitemap_urls, article_from, article_to)

            records_by_date: dict[date, LossesRecordPayload] = {}
            for url in candidate_urls:
                try:
                    html = await self._fetch_text(client, url)
                    losses_date, daily_losses, cumulative_total, raw_text = self._parse_personnel_losses(
                        html
                    )
                except Exception as exc:
                    logger.warning(
                        "losses_adapter_parse_failed",
                        extra={"url": url, "error": str(exc)},
                    )
                    continue

                if not (from_date <= losses_date <= to_date):
                    continue

                records_by_date[losses_date] = LossesRecordPayload(
                    date=losses_date,
                    personnel_losses=daily_losses,
                    source_name=LOSSES_SOURCE_NAME,
                    source_url=url,
                    raw_payload={
                        "reported_daily_losses": daily_losses,
                        "reported_cumulative_total": cumulative_total,
                    },
                    raw_text=raw_text[:5000],
                )

        return [records_by_date[item_date] for item_date in sorted(records_by_date)]


def _daterange(from_date: date, to_date: date) -> list[date]:
    current = from_date
    values: list[date] = []
    while current <= to_date:
        values.append(current)
        current += timedelta(days=1)
    return values
