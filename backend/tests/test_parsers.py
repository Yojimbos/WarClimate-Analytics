from __future__ import annotations

from datetime import date

from app.services.adapters.mod_losses import ModOfficialLossesAdapter


def test_mod_parser_extracts_daily_losses_from_current_article_format() -> None:
    html = """
    <html>
      <body>
        <h1>Total russian combat losses in Ukraine as of April 12, 2026</h1>
        <p>12 April, 2026, 7:32 AM EEST</p>
        <p>Total russian military losses on April 11, 2026: 1,070 personnel, 2,081 UAVs.</p>
        <p>Personnel:</p>
        <ul>
          <li>approximately 1 311 180 (+1 070) persons.</li>
        </ul>
      </body>
    </html>
    """

    losses_date, daily_losses, cumulative_total, text = ModOfficialLossesAdapter._parse_personnel_losses(
        html
    )

    assert losses_date == date(2026, 4, 11)
    assert daily_losses == 1070
    assert cumulative_total == 1311180
    assert "Personnel" in text


def test_mod_parser_extracts_daily_losses_from_older_article_format() -> None:
    html = """
    <html>
      <body>
        <h1>The estimated combat losses of the enemy as of January 18, 2026</h1>
        <p>18 January, 2026, 7:00 AM EEST</p>
        <ul>
          <li>personnel: about 1 226 420 (+830) persons;</li>
        </ul>
      </body>
    </html>
    """

    losses_date, daily_losses, cumulative_total, _ = ModOfficialLossesAdapter._parse_personnel_losses(
        html
    )

    assert losses_date == date(2026, 1, 17)
    assert daily_losses == 830
    assert cumulative_total == 1226420


def test_mod_sitemap_filter_keeps_relevant_official_news_urls() -> None:
    urls = [
        "https://mod.gov.ua/en/news/total-russian-combat-losses-in-ukraine-as-of-april-12-2026",
        "https://mod.gov.ua/en/news/combat-losses-of-the-enemy-as-of-february-18-2026",
        "https://mod.gov.ua/en/news/the-estimated-combat-losses-of-russians-over-the-last-day-880-persons-261-ua-vs-and-42-artillery-systems",
        "https://mod.gov.ua/en/news/ukraine-holds-talks-with-raytheon-and-diehl-defence",
        "https://mod.gov.ua/news/bojovi-vtrati-voroga-na-11-bereznya-2026-roku",
    ]

    candidates = ModOfficialLossesAdapter._candidate_article_urls(
        urls,
        from_date=date(2026, 1, 1),
        to_date=date(2026, 4, 18),
    )

    assert len(candidates) == 2
