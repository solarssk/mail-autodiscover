"""Tests for configuration and SettingsProvider."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from app.config import Authentication, DomainMailSettings, EnvSettingsProvider, Settings
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


def test_trusted_proxy_ips_parsed_as_networks() -> None:
    settings = make_settings(trusted_proxy_ips="127.0.0.1, 10.0.0.0/8 ,10.0.0.1")
    assert len(settings.trusted_proxy_networks) == 3


def test_access_log_skip_paths_parsed() -> None:
    settings = make_settings(access_log_skip_paths="/health, /favicon.ico")
    assert settings.access_log_skip_paths_set == frozenset({"/health", "/favicon.ico"})


def test_allowed_domains_none_becomes_empty_set() -> None:
    settings = make_settings(allowed_domains=None)
    assert settings.allowed_domains_set == frozenset()


def test_domain_settings_for_returns_none_for_disallowed_domain() -> None:
    settings = make_settings()
    assert settings.domain_settings_for("not-allowed.test") is None


def test_rejects_non_positive_body_limit() -> None:
    with pytest.raises(ValidationError, match="must be greater than 0"):
        make_settings(max_request_body_bytes=0)


def test_default_config_file_selects_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONFIG_FILE", raising=False)
    settings = Settings(_env_file=None, app_env="test")
    assert settings.config_file == ""
    assert not settings.domain_configs


@pytest.mark.parametrize("config_file", ["", "   "])
def test_empty_config_file_selects_env(config_file: str) -> None:
    settings = make_settings(config_file=config_file)
    assert settings.domain_settings_for("example.com") is not None
    assert not settings.domain_configs


def _connection_settings(
    tmp_path: Path, mode: str, protocol: str, field: str, value: object
) -> Settings:
    if mode == "env":
        return make_settings(**{f"{protocol}_{field}": value})
    profile = DomainMailSettings.from_env_settings(make_settings()).model_dump(mode="json")
    profile[protocol][field] = value
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump({"domains": {"example.com": profile}}), encoding="utf-8")
    return make_settings(config_file=str(path))


@pytest.mark.parametrize("mode", ["env", "yaml"])
@pytest.mark.parametrize("protocol", ["imap", "smtp", "pop3"])
@pytest.mark.parametrize("port", [0, -1, 65536])
def test_invalid_mail_ports_prevent_startup(
    tmp_path: Path, mode: str, protocol: str, port: int
) -> None:
    with pytest.raises(ValidationError, match="port"):
        _connection_settings(tmp_path, mode, protocol, "port", port)


@pytest.mark.parametrize("mode", ["env", "yaml"])
@pytest.mark.parametrize("port", [1, 65535])
def test_mail_port_boundaries_are_valid(tmp_path: Path, mode: str, port: int) -> None:
    settings = _connection_settings(tmp_path, mode, "imap", "port", port)
    profile = settings.domain_settings_for("example.com")
    assert profile is not None
    assert profile.imap.port == port


@pytest.mark.parametrize("mode", ["env", "yaml"])
@pytest.mark.parametrize(
    "host",
    [
        "",
        " ",
        "mail.example.com\n",
        "mail.exa\u200bmple.com",
        "https://mail.example.com",
        "mail.example.com:993",
        "mail.example.com/path",
        "user@mail.example.com",
        "-mail.example.com",
        "a..b",
        ".",
        "a_b.example.com",
    ],
)
def test_invalid_mail_hosts_prevent_startup(tmp_path: Path, mode: str, host: str) -> None:
    with pytest.raises(ValidationError, match="host"):
        _connection_settings(tmp_path, mode, "imap", "host", host)


@pytest.mark.parametrize("mode", ["env", "yaml"])
@pytest.mark.parametrize(
    "host", ["mail", "mail.example.com.", "192.168.1.5", "2001:db8::5", "xn--bcher-kva.example"]
)
def test_internal_and_ip_mail_hosts_remain_valid(tmp_path: Path, mode: str, host: str) -> None:
    settings = _connection_settings(tmp_path, mode, "imap", "host", host)
    profile = settings.domain_settings_for("example.com")
    assert profile is not None
    assert profile.imap.host == host


@pytest.mark.parametrize("mode", ["env", "yaml"])
def test_unicode_mail_hosts_are_returned_as_punycode(tmp_path: Path, mode: str) -> None:
    settings = _connection_settings(tmp_path, mode, "imap", "host", "b\u00fccher.example")
    profile = settings.domain_settings_for("example.com")
    assert profile is not None
    assert profile.imap.host == "xn--bcher-kva.example"


@pytest.mark.parametrize("mode", ["env", "yaml"])
@pytest.mark.parametrize("authentication", list(Authentication))
def test_documented_authentication_values_remain_valid(
    tmp_path: Path, mode: str, authentication: Authentication
) -> None:
    settings = _connection_settings(tmp_path, mode, "smtp", "authentication", authentication.value)
    profile = settings.domain_settings_for("example.com")
    assert profile is not None
    assert profile.smtp.authentication == authentication


@pytest.mark.parametrize("mode", ["env", "yaml"])
@pytest.mark.parametrize("authentication", ["", "password", "password-cleartext\n"])
def test_unknown_authentication_prevents_startup(
    tmp_path: Path, mode: str, authentication: str
) -> None:
    with pytest.raises(ValidationError, match="[Aa]uthentication"):
        _connection_settings(tmp_path, mode, "smtp", "authentication", authentication)


@pytest.mark.parametrize("mode", ["env", "yaml"])
@pytest.mark.parametrize("protocol", ["imap", "pop3"])
def test_smtp_only_authentication_is_rejected_for_incoming_servers(
    tmp_path: Path, mode: str, protocol: str
) -> None:
    with pytest.raises(ValidationError, match="only valid for SMTP"):
        _connection_settings(tmp_path, mode, protocol, "authentication", "SMTP-after-POP")


@pytest.mark.parametrize("port", [0, 65536])
def test_invalid_container_port_prevents_startup(port: int) -> None:
    with pytest.raises(ValidationError, match="container_port"):
        make_settings(container_port=port)


def test_yaml_ignores_unused_env_connection_values(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    profile = DomainMailSettings.from_env_settings(make_settings()).model_dump(mode="json")
    path.write_text(yaml.safe_dump({"domains": {"example.com": profile}}), encoding="utf-8")
    settings = make_settings(
        config_file=str(path), imap_host="", imap_port=0, imap_authentication="unknown"
    )
    resolved = settings.domain_settings_for("example.com")
    assert resolved is not None
    assert resolved.imap.port == 993
