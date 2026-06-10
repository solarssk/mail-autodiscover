"""Tests for Thunderbird Autoconfig endpoints."""

from fastapi.testclient import TestClient

from app.main import create_app
from app.security import reset_rate_limit_store
from tests.conftest import FixedSettingsProvider, make_settings


def test_thunderbird_returns_200(client: TestClient) -> None:
    response = client.get("/mail/config-v1.1.xml", params={"emailaddress": "user@example.com"})
    assert response.status_code == 200


def test_thunderbird_content_type(client: TestClient) -> None:
    response = client.get("/mail/config-v1.1.xml", params={"emailaddress": "user@example.com"})
    assert response.headers["content-type"] == "application/xml; charset=utf-8"


def test_thunderbird_contains_imap(client: TestClient) -> None:
    response = client.get("/mail/config-v1.1.xml", params={"emailaddress": "user@example.com"})
    assert "<hostname>mail.example.com</hostname>" in response.text
    assert "<port>993</port>" in response.text
    assert 'type="imap"' in response.text


def test_thunderbird_contains_smtp(client: TestClient) -> None:
    response = client.get("/mail/config-v1.1.xml", params={"emailaddress": "user@example.com"})
    assert "<port>587</port>" in response.text
    assert 'type="smtp"' in response.text


def test_thunderbird_username_is_full_email(client: TestClient) -> None:
    response = client.get("/mail/config-v1.1.xml", params={"emailaddress": "user@example.com"})
    assert "<username>user@example.com</username>" in response.text


def test_thunderbird_unknown_domain_neutral_error(client: TestClient) -> None:
    response = client.get("/mail/config-v1.1.xml", params={"emailaddress": "user@evil.org"})
    assert response.status_code == 404
    assert "evil.org" not in response.text
    assert "ALLOWED_DOMAINS" not in response.text


def test_thunderbird_missing_emailaddress(client: TestClient) -> None:
    response = client.get("/mail/config-v1.1.xml")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid request"}


def test_thunderbird_xml_escape() -> None:
    reset_rate_limit_store()
    settings = make_settings(
        mail_display_name='Test <script> & Co',
        mail_display_short_name="T&M",
    )
    app = create_app(FixedSettingsProvider(settings))
    with TestClient(app) as c:
        response = c.get(
            "/mail/config-v1.1.xml",
            params={"emailaddress": "user@example.com"},
        )
    assert "&lt;script&gt;" in response.text
    assert "&amp;" in response.text
    assert "T&amp;M" in response.text
    assert "<script>" not in response.text


def test_thunderbird_wellknown_endpoint(client: TestClient) -> None:
    response = client.get(
        "/.well-known/autoconfig/mail/config-v1.1.xml",
        params={"emailaddress": "user@example.com"},
    )
    assert response.status_code == 200
    assert "clientConfig" in response.text


def test_thunderbird_disabled() -> None:
    reset_rate_limit_store()
    settings = make_settings(thunderbird_enabled=False)
    app = create_app(FixedSettingsProvider(settings))
    with TestClient(app) as c:
        response = c.get("/mail/config-v1.1.xml", params={"emailaddress": "user@example.com"})
    assert response.status_code == 404
