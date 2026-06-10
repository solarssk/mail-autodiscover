"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.security import reset_rate_limit_store


class FixedSettingsProvider:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def get_settings(self) -> Settings:
        return self._settings


def make_settings(**overrides: object) -> Settings:
    defaults = {
        "app_name": "mail-autodiscover",
        "app_env": "test",
        "public_base_url": "http://localhost:8000",
        "allowed_domains": "example.com,example.pl",
        "mail_display_name": "Example Mail",
        "mail_display_short_name": "Example",
        "imap_host": "mail.example.com",
        "imap_port": 993,
        "imap_socket_type": "SSL",
        "imap_authentication": "password-cleartext",
        "smtp_host": "mail.example.com",
        "smtp_port": 587,
        "smtp_socket_type": "STARTTLS",
        "smtp_authentication": "password-cleartext",
        "username_format": "email",
        "container_port": 8000,
        "trust_proxy_headers": False,
        "log_level": "WARNING",
        "max_request_body_bytes": 16384,
        "rate_limit_enabled": False,
        "rate_limit_per_minute": 60,
        "pop3_enabled": False,
        "outlook_enabled": True,
        "thunderbird_enabled": True,
        "return_404_for_unknown_domain": True,
        "disable_access_log": True,
        "security_headers_enabled": True,
    }
    defaults.update(overrides)
    return Settings(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def settings() -> Settings:
    return make_settings()


@pytest.fixture
def client(settings: Settings) -> TestClient:
    reset_rate_limit_store()
    app = create_app(FixedSettingsProvider(settings))
    with TestClient(app) as c:
        yield c


OUTLOOK_REQUEST_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/requestschema/2006">
  <Request>
    <EMailAddress>{email}</EMailAddress>
    <AcceptableResponseSchema>
      http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a
    </AcceptableResponseSchema>
  </Request>
</Autodiscover>"""
