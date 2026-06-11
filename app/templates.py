"""XML response generators for Thunderbird and Outlook autodiscover."""

from __future__ import annotations

from xml.sax.saxutils import escape

from app.config import Settings, SocketType
from app.email_utils import ValidatedEmail, build_username


def _esc(value: str | int) -> str:
    """XML-escape a value for safe inclusion in response bodies."""
    return escape(str(value))


def _outlook_ssl_on(socket_type: SocketType) -> str:
    """Map socket type to Outlook Autodiscover SSL on/off values."""
    return "on" if socket_type in (SocketType.SSL, SocketType.STARTTLS) else "off"


def thunderbird_autoconfig(validated: ValidatedEmail, settings: Settings) -> str:
    """Build Thunderbird clientConfig XML for a validated mailbox."""
    username = build_username(validated, settings.username_format)
    domain = validated.domain

    pop3_block = ""
    if settings.pop3_enabled:
        pop3_block = f"""
    <incomingServer type="pop3">
      <hostname>{_esc(settings.pop3_host)}</hostname>
      <port>{_esc(settings.pop3_port)}</port>
      <socketType>{_esc(settings.pop3_socket_type.value)}</socketType>
      <authentication>{_esc(settings.pop3_authentication)}</authentication>
      <username>{_esc(username)}</username>
    </incomingServer>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<clientConfig version="1.1">
  <emailProvider id="{_esc(domain)}">
    <domain>{_esc(domain)}</domain>
    <displayName>{_esc(settings.mail_display_name)}</displayName>
    <displayShortName>{_esc(settings.mail_display_short_name)}</displayShortName>

    <incomingServer type="imap">
      <hostname>{_esc(settings.imap_host)}</hostname>
      <port>{_esc(settings.imap_port)}</port>
      <socketType>{_esc(settings.imap_socket_type.value)}</socketType>
      <authentication>{_esc(settings.imap_authentication)}</authentication>
      <username>{_esc(username)}</username>
    </incomingServer>{pop3_block}

    <outgoingServer type="smtp">
      <hostname>{_esc(settings.smtp_host)}</hostname>
      <port>{_esc(settings.smtp_port)}</port>
      <socketType>{_esc(settings.smtp_socket_type.value)}</socketType>
      <authentication>{_esc(settings.smtp_authentication)}</authentication>
      <username>{_esc(username)}</username>
    </outgoingServer>
  </emailProvider>
</clientConfig>
"""


def outlook_autodiscover(validated: ValidatedEmail, settings: Settings) -> str:
    """Build Outlook Autodiscover XML with IMAP and SMTP settings."""
    username = build_username(validated, settings.username_format)
    imap_ssl = _outlook_ssl_on(settings.imap_socket_type)
    smtp_ssl = _outlook_ssl_on(settings.smtp_socket_type)

    return f"""<?xml version="1.0" encoding="utf-8"?>
<Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/responseschema/2006">
  <Response xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a">
    <Account>
      <AccountType>email</AccountType>
      <Action>settings</Action>

      <Protocol>
        <Type>IMAP</Type>
        <Server>{_esc(settings.imap_host)}</Server>
        <Port>{_esc(settings.imap_port)}</Port>
        <DomainRequired>off</DomainRequired>
        <LoginName>{_esc(username)}</LoginName>
        <SPA>off</SPA>
        <SSL>{imap_ssl}</SSL>
        <AuthRequired>on</AuthRequired>
      </Protocol>

      <Protocol>
        <Type>SMTP</Type>
        <Server>{_esc(settings.smtp_host)}</Server>
        <Port>{_esc(settings.smtp_port)}</Port>
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
