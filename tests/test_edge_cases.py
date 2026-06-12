"""Edge-case and optional-feature tests."""

from fastapi.testclient import TestClient

from app.main import create_app
from app.security import reset_rate_limit_store
from tests.conftest import OUTLOOK_REQUEST_TEMPLATE, FixedSettingsProvider, make_settings


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_endpoint(client: TestClient) -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_outlook_disabled() -> None:
    reset_rate_limit_store()
    settings = make_settings(outlook_enabled=False)
    app = create_app(FixedSettingsProvider(settings))
    body = OUTLOOK_REQUEST_TEMPLATE.format(email="user@example.com")
    with TestClient(app) as c:
        response = c.post(
            "/autodiscover/autodiscover.xml",
            content=body,
            headers={"Content-Type": "text/xml"},
        )
    assert response.status_code == 404


def test_unknown_domain_returns_400_when_configured() -> None:
    reset_rate_limit_store()
    settings = make_settings(return_404_for_unknown_domain=False)
    app = create_app(FixedSettingsProvider(settings))
    with TestClient(app) as c:
        response = c.get(
            "/mail/config-v1.1.xml",
            params={"emailaddress": "user@evil.org"},
        )
    assert response.status_code == 400
    assert response.json() == {"detail": "Configuration not available"}
    assert "evil.org" not in response.text


def test_security_headers_disabled() -> None:
    reset_rate_limit_store()
    settings = make_settings(security_headers_enabled=False)
    app = create_app(FixedSettingsProvider(settings))
    with TestClient(app) as c:
        response = c.get("/health")
    assert response.headers.get("X-Content-Type-Options") is None
    assert response.headers.get("Cache-Control") is None


def test_ready_not_rate_limited() -> None:
    reset_rate_limit_store()
    settings = make_settings(rate_limit_enabled=True, rate_limit_per_minute=1)
    app = create_app(FixedSettingsProvider(settings))
    with TestClient(app) as c:
        for _ in range(4):
            assert c.get("/ready").status_code == 200


def test_thunderbird_pop3_block_when_enabled() -> None:
    reset_rate_limit_store()
    settings = make_settings(
        pop3_enabled=True,
        pop3_host="pop.example.com",
        pop3_port=995,
    )
    app = create_app(FixedSettingsProvider(settings))
    with TestClient(app) as c:
        response = c.get(
            "/mail/config-v1.1.xml",
            params={"emailaddress": "user@example.com"},
        )
    assert response.status_code == 200
    assert 'type="pop3"' in response.text
    assert "<hostname>pop.example.com</hostname>" in response.text
    assert "<port>995</port>" in response.text


def test_rate_limit_uses_x_forwarded_for_when_trusted() -> None:
    reset_rate_limit_store()
    settings = make_settings(
        rate_limit_enabled=True,
        rate_limit_per_minute=2,
        trust_proxy_headers=True,
        trusted_proxy_ips="127.0.0.1/32",
    )
    app = create_app(FixedSettingsProvider(settings))
    headers = {"X-Forwarded-For": "203.0.113.10"}
    with TestClient(app) as c:
        assert c.get("/robots.txt", headers=headers).status_code == 200
        assert c.get("/robots.txt", headers=headers).status_code == 200
        assert c.get("/robots.txt", headers=headers).status_code == 429
