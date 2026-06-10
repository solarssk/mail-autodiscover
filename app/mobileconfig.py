"""Apple Configuration Profile (.mobileconfig) generator for IMAP mail accounts."""

from __future__ import annotations

import plistlib
import uuid

from app.config import Settings, SocketType
from app.email_utils import ValidatedEmail, build_username

MOBILECONFIG_CONTENT_TYPE = "application/x-apple-aspen-config; charset=utf-8"


def _use_ssl(socket_type: SocketType) -> bool:
    return socket_type in (SocketType.SSL, SocketType.STARTTLS)


def apple_mail_mobileconfig(validated: ValidatedEmail, settings: Settings) -> bytes:
    """Build unsigned com.apple.mail.managed configuration profile (no passwords)."""
    username = build_username(validated, settings.username_format)
    mail_uuid = str(uuid.uuid4()).upper()
    root_uuid = str(uuid.uuid4()).upper()

    mail_payload: dict[str, object] = {
        "PayloadType": "com.apple.mail.managed",
        "PayloadVersion": 1,
        "PayloadIdentifier": f"com.mail-autodiscover.mail.{mail_uuid}",
        "PayloadUUID": mail_uuid,
        "PayloadDisplayName": settings.mail_display_name,
        "EmailAccountDescription": settings.mail_display_name,
        "EmailAccountName": settings.mail_display_short_name,
        "EmailAccountType": "EmailTypeIMAP",
        "EmailAddress": validated.email,
        "IncomingMailServerHostName": settings.imap_host,
        "IncomingMailServerPortNumber": settings.imap_port,
        "IncomingMailServerUseSSL": _use_ssl(settings.imap_socket_type),
        "IncomingMailServerAuthentication": "EmailAuthPassword",
        "IncomingMailServerUsername": username,
        "OutgoingMailServerHostName": settings.smtp_host,
        "OutgoingMailServerPortNumber": settings.smtp_port,
        "OutgoingMailServerUseSSL": _use_ssl(settings.smtp_socket_type),
        "OutgoingMailServerAuthentication": "EmailAuthPassword",
        "OutgoingMailServerUsername": username,
        "OutgoingPasswordSameAsIncomingPassword": True,
    }

    profile: dict[str, object] = {
        "PayloadType": "Configuration",
        "PayloadVersion": 1,
        "PayloadIdentifier": f"com.mail-autodiscover.profile.{root_uuid}",
        "PayloadUUID": root_uuid,
        "PayloadDisplayName": settings.mail_display_name,
        "PayloadDescription": "Mail account settings for Apple Mail",
        "PayloadContent": [mail_payload],
    }

    return plistlib.dumps(profile, fmt=plistlib.FMT_XML)
