"""Application configuration via environment variables."""

from __future__ import annotations

import ipaddress
from enum import StrEnum
from functools import lru_cache
from typing import Protocol

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class UsernameFormat(StrEnum):
    EMAIL = "email"
    LOCALPART = "localpart"


class SocketType(StrEnum):
    SSL = "SSL"
    STARTTLS = "STARTTLS"
    PLAIN = "plain"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = Field(default="mail-autodiscover", alias="APP_NAME")
    app_env: str = Field(default="production", alias="APP_ENV")
    public_base_url: str = Field(default="http://localhost:8000", alias="PUBLIC_BASE_URL")

    allowed_domains: str = Field(default="example.com", alias="ALLOWED_DOMAINS")

    mail_display_name: str = Field(default="Example Mail", alias="MAIL_DISPLAY_NAME")
    mail_display_short_name: str = Field(default="Example", alias="MAIL_DISPLAY_SHORT_NAME")

    imap_host: str = Field(default="mail.example.com", alias="IMAP_HOST")
    imap_port: int = Field(default=993, alias="IMAP_PORT")
    imap_socket_type: SocketType = Field(default=SocketType.SSL, alias="IMAP_SOCKET_TYPE")
    imap_authentication: str = Field(default="password-cleartext", alias="IMAP_AUTHENTICATION")

    smtp_host: str = Field(default="mail.example.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_socket_type: SocketType = Field(default=SocketType.STARTTLS, alias="SMTP_SOCKET_TYPE")
    smtp_authentication: str = Field(default="password-cleartext", alias="SMTP_AUTHENTICATION")

    username_format: UsernameFormat = Field(default=UsernameFormat.EMAIL, alias="USERNAME_FORMAT")

    container_port: int = Field(default=8000, alias="CONTAINER_PORT")

    trust_proxy_headers: bool = Field(default=True, alias="TRUST_PROXY_HEADERS")
    trusted_proxy_ips: str = Field(
        default="",
        validation_alias=AliasChoices("TRUSTED_PROXY_IPS", "FORWARDED_ALLOW_IPS"),
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    max_request_body_bytes: int = Field(default=16384, alias="MAX_REQUEST_BODY_BYTES")
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")

    pop3_enabled: bool = Field(default=False, alias="POP3_ENABLED")
    pop3_host: str = Field(default="mail.example.com", alias="POP3_HOST")
    pop3_port: int = Field(default=995, alias="POP3_PORT")
    pop3_socket_type: SocketType = Field(default=SocketType.SSL, alias="POP3_SOCKET_TYPE")
    pop3_authentication: str = Field(default="password-cleartext", alias="POP3_AUTHENTICATION")

    outlook_enabled: bool = Field(default=True, alias="OUTLOOK_ENABLED")
    thunderbird_enabled: bool = Field(default=True, alias="THUNDERBIRD_ENABLED")

    return_404_for_unknown_domain: bool = Field(
        default=True, alias="RETURN_404_FOR_UNKNOWN_DOMAIN"
    )
    disable_access_log: bool = Field(default=False, alias="DISABLE_ACCESS_LOG")
    access_log_skip_paths: str = Field(
        default="/health,/favicon.ico,/apple-touch-icon.png",
        alias="ACCESS_LOG_SKIP_PATHS",
    )
    security_headers_enabled: bool = Field(default=True, alias="SECURITY_HEADERS_ENABLED")

    apple_mobileconfig_enabled: bool = Field(default=True, alias="APPLE_MOBILECONFIG_ENABLED")

    @field_validator("allowed_domains", mode="before")
    @classmethod
    def parse_allowed_domains(cls, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @property
    def allowed_domains_set(self) -> frozenset[str]:
        domains = {d.strip().lower() for d in self.allowed_domains.split(",") if d.strip()}
        return frozenset(domains)

    @property
    def access_log_skip_paths_set(self) -> frozenset[str]:
        paths = {p.strip() for p in self.access_log_skip_paths.split(",") if p.strip()}
        return frozenset(paths)

    @property
    def trusted_proxy_networks(
        self,
    ) -> tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...]:
        """Parsed CIDR/IP entries from TRUSTED_PROXY_IPS (empty = trust any peer when enabled)."""
        entries: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
        for part in self.trusted_proxy_ips.split(","):
            token = part.strip()
            if not token:
                continue
            try:
                if "/" in token:
                    entries.append(ipaddress.ip_network(token, strict=False))
                else:
                    prefix = "128" if ":" in token else "32"
                    entries.append(ipaddress.ip_network(f"{token}/{prefix}", strict=False))
            except ValueError:
                continue
        return tuple(entries)

    @field_validator("imap_socket_type", "smtp_socket_type", "pop3_socket_type", mode="before")
    @classmethod
    def normalize_socket_type(cls, value: object) -> object:
        if isinstance(value, str):
            return value.upper() if value.lower() != "plain" else "plain"
        return value


class SettingsProvider(Protocol):
    def get_settings(self) -> Settings: ...


class EnvSettingsProvider:
    """Reads configuration from environment variables (MVP default)."""

    def get_settings(self) -> Settings:
        return get_settings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
