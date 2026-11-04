"""Tests for landing page, static assets, and robots.txt."""

import struct
from html.parser import HTMLParser

from fastapi.testclient import TestClient

from app.landing import landing_page_html
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
    assert "default-src 'none'" in response.headers["content-security-policy"]
    assert "<script" not in text
    assert "<form" not in text


def test_landing_escapes_app_name() -> None:
    html = landing_page_html('<img src=x onerror=alert(1)> & "Mail"')
    assert "<img src=x" not in html
    assert '&lt;img src=x onerror=alert(1)&gt; &amp; "Mail"' in html


def test_landing_has_accessible_static_content() -> None:
    html = landing_page_html("Mail")
    assert '<html lang="en">' in html
    assert '<main id="main" tabindex="-1">' in html
    assert 'aria-labelledby="formats-heading"' in html
    assert "a:focus-visible" in html
    assert "prefers-color-scheme: dark" in html
    assert "background: var(--page)" in html
    assert "opacity:" not in html
    assert "maximum-scale" not in html
    assert "user-scalable" not in html
    assert html.count("Mail client<br>configuration.") == 1
    assert 'class="eyebrow"' not in html
    assert 'class="number"' not in html


def test_protocols_are_readable_without_scripts_or_styles() -> None:
    class TextReader(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.in_style = False
            self.parts: list[str] = []

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            if tag == "style":
                self.in_style = True

        def handle_endtag(self, tag: str) -> None:
            if tag == "style":
                self.in_style = False

        def handle_data(self, data: str) -> None:
            if not self.in_style:
                self.parts.append(data)

    reader = TextReader()
    reader.feed(landing_page_html("Mail"))
    text = " ".join(" ".join(reader.parts).split())
    for client, method, path in [
        ("Outlook", "POST", "/autodiscover/autodiscover.xml"),
        ("Thunderbird", "GET", "/mail/config-v1.1.xml"),
        ("Apple Mail", "GET", "/mail/ios.mobileconfig"),
    ]:
        assert client in text
        assert f"{method} {path}" in text
    assert "does not ask for, store, or verify mailbox passwords" in text


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
    assert touch.content[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", touch.content[16:24]) == (180, 180)
    reserved, image_type, count = struct.unpack("<HHH", fav.content[:6])
    assert (reserved, image_type, count) == (0, 1, 3)
    sizes = [tuple(fav.content[6 + index * 16 : 8 + index * 16]) for index in range(count)]
    assert sizes == [(16, 16), (32, 32), (48, 48)]
