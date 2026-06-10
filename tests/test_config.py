"""Tests for configuration and SettingsProvider."""

from app.config import EnvSettingsProvider, Settings
from tests.conftest import FixedSettingsProvider, make_settings


def test_settings_allowed_domains_parsed() -> None:
    settings = make_settings(allowed_domains="Example.COM, example.pl")
    assert settings.allowed_domains_set == frozenset({"example.com", "example.pl"})


def test_settings_provider_returns_settings() -> None:
    settings = make_settings()
    provider = FixedSettingsProvider(settings)
    assert provider.get_settings() is settings


def test_env_settings_provider() -> None:
    provider = EnvSettingsProvider()
    result = provider.get_settings()
    assert isinstance(result, Settings)


def test_socket_type_normalization() -> None:
    settings = make_settings(imap_socket_type="ssl", smtp_socket_type="starttls")
    assert settings.imap_socket_type.value == "SSL"
    assert settings.smtp_socket_type.value == "STARTTLS"
