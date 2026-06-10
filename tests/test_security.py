"""Tests for security features."""

import logging

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.security import reset_rate_limit_store
from tests.conftest import FixedSettingsProvider, make_settings


def test_root_does_not_expose_domains_or_hosts(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "status" in data
    assert "example.com" not in str(data)
    assert "mail.example.com" not in str(data)
    assert "allowed" not in str(data).lower()


def test_security_headers_present(client: TestClient) -> None:
    response = client.get("/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("Referrer-Policy") == "no-referrer"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Cache-Control") == "no-store"


def test_rate_limit_when_enabled() -> None:
    reset_rate_limit_store()
    settings = make_settings(rate_limit_enabled=True, rate_limit_per_minute=3)
    app = create_app(FixedSettingsProvider(settings))
    with TestClient(app) as c:
        for _ in range(3):
            response = c.get("/health")
            assert response.status_code == 200
        response = c.get("/health")
        assert response.status_code == 429
        assert response.json() == {"detail": "Too many requests"}


def test_logs_do_not_contain_full_email(caplog: pytest.LogCaptureFixture) -> None:
    reset_rate_limit_store()
    settings = make_settings(disable_access_log=False, log_level="INFO")
    app = create_app(FixedSettingsProvider(settings))

    with caplog.at_level(logging.INFO, logger="mail_autodiscover.access"):
        with TestClient(app) as c:
            c.get("/mail/config-v1.1.xml", params={"emailaddress": "secret.user@example.com"})

    log_text = " ".join(r.message for r in caplog.records)
    assert "secret.user@example.com" not in log_text
    assert "domain_allowed=true" in log_text
