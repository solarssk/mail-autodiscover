"""XML response generators for Thunderbird and Outlook autodiscover."""

from __future__ import annotations

from xml.sax.saxutils import escape

from app.config import DomainMailSettings, Settings, SocketType, UsernameFormat
from app.email_utils import ValidatedEmail, build_username


def _esc(value: str | int) -> str:
    """XML-escape a value for safe inclusion in response bodies."""
    return escape(str(value))


def _outlook_ssl_on(socket_type: SocketType) -> str:
    """Map socket type to Outlook Autodiscover SSL on/off values."""
    return "on" if socket_type in (SocketType.SSL, SocketType.STARTTLS) else "off"


def _resolve_domain_settings(
    settings_or_domain: Settings | DomainMailSettings,
) -> tuple[DomainMailSettings, UsernameFormat]:
    """Normalize legacy Settings input and new per-domain input to one shape."""
    if isinstance(settings_or_domain, Settings):
        return (
            DomainMailSettings.from_env_settings(settings_or_domain),
            settings_or_domain.username_format,
        )
    return settings_or_domain, UsernameFormat.EMAIL


def thunderbird_autoconfig(
    validated: ValidatedEmail,
    settings_or_domain: Settings | DomainMailSettings,
    username_format: UsernameFormat | None = None,
) -> str:
    """Build Thunderbird clientConfig XML for a validated mailbox."""
    domain_settings, default_username_format = _resolve_domain_settings(settings_or_domain)
    effective_username_format = username_format or default_username_format
    username = build_username(validated, effective_username_format)
    domain = validated.domain

    pop3_block = ""
    if domain_settings.pop3 and domain_settings.pop3.enabled:
        pop3_block = f"""
    <incomingServer type="pop3">
      <hostname>{_esc(domain_settings.pop3.host)}</hostname>
      <port>{_esc(domain_settings.pop3.port)}</port>
      <socketType>{_esc(domain_settings.pop3.socket_type.value)}</socketType>
      <authentication>{_esc(domain_settings.pop3.authentication)}</authentication>
      <username>{_esc(username)}</username>
    </incomingServer>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<clientConfig version="1.1">
  <emailProvider id="{_esc(domain)}">
    <domain>{_esc(domain)}</domain>
    <displayName>{_esc(domain_settings.display_name)}</displayName>
    <displayShortName>{_esc(domain_settings.display_short_name)}</displayShortName>

    <incomingServer type="imap">
      <hostname>{_esc(domain_settings.imap.host)}</hostname>
      <port>{_esc(domain_settings.imap.port)}</port>
      <socketType>{_esc(domain_settings.imap.socket_type.value)}</socketType>
      <authentication>{_esc(domain_settings.imap.authentication)}</authentication>
      <username>{_esc(username)}</username>
    </incomingServer>{pop3_block}

    <outgoingServer type="smtp">
      <hostname>{_esc(domain_settings.smtp.host)}</hostname>
      <port>{_esc(domain_settings.smtp.port)}</port>
      <socketType>{_esc(domain_settings.smtp.socket_type.value)}</socketType>
      <authentication>{_esc(domain_settings.smtp.authentication)}</authentication>
      <username>{_esc(username)}</username>
    </outgoingServer>
  </emailProvider>
</clientConfig>
"""


def outlook_autodiscover(
    validated: ValidatedEmail,
    settings_or_domain: Settings | DomainMailSettings,
    username_format: UsernameFormat | None = None,
) -> str:
    """Build Outlook Autodiscover XML with IMAP and SMTP settings."""
    domain_settings, default_username_format = _resolve_domain_settings(settings_or_domain)
    effective_username_format = username_format or default_username_format
    username = build_username(validated, effective_username_format)
    imap_ssl = _outlook_ssl_on(domain_settings.imap.socket_type)
    smtp_ssl = _outlook_ssl_on(domain_settings.smtp.socket_type)

    return f"""<?xml version="1.0" encoding="utf-8"?>
<Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/responseschema/2006">
  <Response xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a">
    <Account>
      <AccountType>email</AccountType>
      <Action>settings</Action>

      <Protocol>
        <Type>IMAP</Type>
        <Server>{_esc(domain_settings.imap.host)}</Server>
        <Port>{_esc(domain_settings.imap.port)}</Port>
        <DomainRequired>off</DomainRequired>
        <LoginName>{_esc(username)}</LoginName>
        <SPA>off</SPA>
        <SSL>{imap_ssl}</SSL>
        <AuthRequired>on</AuthRequired>
      </Protocol>

      <Protocol>
        <Type>SMTP</Type>
        <Server>{_esc(domain_settings.smtp.host)}</Server>
        <Port>{_esc(domain_settings.smtp.port)}</Port>
        <DomainRequired>off</DomainRequired>
        <LoginName>{_esc(username)}</LoginName>
        <SPA>off</SPA>
        <SSL>{smtp_ssl}</SSL>
        <AuthRequired>on</AuthRequired>
        <UsePOPAuth>off</UsePOPAuth>
        <SMTPLast>off</SMTPLast>
      </Protocol>
    </Account>
  </Response>
</Autodiscover>
"""


def outlook_get_neutral_response() -> str:
    """Return a neutral Outlook error response for unauthenticated GET probes."""
    return """<?xml version="1.0" encoding="utf-8"?>
<Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/responseschema/2006">
  <Response>
    <Error Code="600" Message="Invalid request" />
  </Response>
</Autodiscover>
"""
