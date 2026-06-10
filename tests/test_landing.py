"""Tests for landing page, static assets, and robots.txt."""

from fastapi.testclient import TestClient

from app.main import create_app
from tests.conftest import FixedSettingsProvider, make_settings


def test_root_returns_html_without_sensitive_data() -> None:
    settings = make_settings(
        allowed_domains="secret.example.com",
        imap_host="mail.secret.example.com",
    )
    app = create_app(FixedSettingsProvider(settings))
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    text = response.text.lower()
    assert "autodiscover" in text
    assert "secret.example.com" not in response.text
    assert "mail.secret" not in response.text


def test_robots_txt_disallows_all() -> None:
    app = create_app(FixedSettingsProvider(make_settings()))
    with TestClient(app) as client:
        response = client.get("/robots.txt")
    assert response.status_code == 200
    assert "Disallow: /" in response.text


def test_favicon_and_apple_touch_icon() -> None:
    app = create_app(FixedSettingsProvider(make_settings()))
    with TestClient(app) as client:
        fav = client.get("/favicon.ico")
        touch = client.get("/apple-touch-icon.png")
    assert fav.status_code == 200
    assert fav.headers["content-type"] == "image/x-icon"
    assert touch.status_code == 200
    assert touch.headers["content-type"] == "image/png"
    assert len(touch.content) > 100
