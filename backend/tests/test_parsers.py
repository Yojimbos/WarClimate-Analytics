from __future__ import annotations

from app.services.adapters.mod_losses import ModOfficialLossesAdapter


def test_mod_parser_extracts_personnel_losses() -> None:
    html = "<html><body><p>personnel - about 938,970 persons</p></body></html>"
    value, text = ModOfficialLossesAdapter._parse_personnel_losses(html)
    assert value == 938970
    assert "personnel" in text
