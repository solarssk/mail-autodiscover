"""Tests for Apple .mobileconfig profile generation."""

import plistlib

from fastapi.testclient import TestClient

from app.main import create_app
from tests.conftest import FixedSettingsProvider, make_settings


def test_mobileconfig_returns_plist_for_allowed_domain() -> None:
    settings = make_settings()
    app = create_app(FixedSettingsProvider(settings))
    with TestClient(app) as client:
        response = client.get(
            "/mail/ios.mobileconfig",
            params={"emailaddress": "user@example.com"},
        )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/x-apple-aspen-config")
    assert "mail-autodiscover.mobileconfig" in response.headers.get("content-disposition", "")

    profile = plistlib.loads(response.content)
    assert profile["PayloadType"] == "Configuration"
    mail = profile["PayloadContent"][0]
    assert mail["PayloadType"] == "com.apple.mail.managed"
    assert mail["EmailAccountType"] == "EmailTypeIMAP"
    assert mail["EmailAddress"] == "user@example.com"
    assert mail["IncomingMailServerHostName"] == "mail.example.com"
    assert mail["IncomingMailServerPortNumber"] == 993
    assert mail["OutgoingMailServerHostName"] == "mail.example.com"
    assert mail["OutgoingMailServerPortNumber"] == 587
    assert "IncomingPassword" not in mail
    assert "OutgoingPassword" not in mail


def test_mobileconfig_unknown_domain_404() -> None:
    settings = make_settings()
    app = create_app(FixedSettingsProvider(settings))
    with TestClient(app) as client:
        response = client.get(
            "/mail/ios.mobileconfig",
            params={"emailaddress": "user@evil.org"},
        )
    assert response.status_code == 404


def test_mobileconfig_wellknown_alias() -> None:
    settings = make_settings()
    app = create_app(FixedSettingsProvider(settings))
    with TestClient(app) as client:
        response = client.get(
            "/.well-known/apple-mail.mobileconfig",
            params={"emailaddress": "user@example.com"},
        )
    assert response.status_code == 200


def test_mobileconfig_disabled() -> None:
    settings = make_settings(apple_mobileconfig_enabled=False)
    app = create_app(FixedSettingsProvider(settings))
    with TestClient(app) as client:
        response = client.get(
            "/mail/ios.mobileconfig",
            params={"emailaddress": "user@example.com"},
        )
    assert response.status_code == 404
