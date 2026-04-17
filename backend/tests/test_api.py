from __future__ import annotations


def test_get_losses(client) -> None:
    response = client.get("/api/v1/losses", params={"from": "2026-04-04", "to": "2026-04-10"})
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_get_weather(client) -> None:
    response = client.get(
        "/api/v1/weather", params={"from": "2026-04-04", "to": "2026-04-10", "location": "kyiv"}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_get_summary(client) -> None:
    response = client.get(
        "/api/v1/summary", params={"from": "2026-04-04", "to": "2026-04-10", "location": "kyiv"}
    )
    assert response.status_code == 200
    assert "cards" in response.json()
