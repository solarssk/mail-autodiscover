"""Apple Configuration Profile (.mobileconfig) generator for IMAP mail accounts."""

from __future__ import annotations

import plistlib
import re
import uuid

from app.config import DomainMailSettings, SocketType, UsernameFormat
from app.email_utils import ValidatedEmail, build_username

MOBILECONFIG_CONTENT_TYPE = "application/x-apple-aspen-config; charset=utf-8"
_PROFILE_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "https://github.com/solarssk/mail-autodiscover")


def _use_ssl(socket_type: SocketType) -> bool:
    """Return whether Apple Mail should enable SSL for the given socket type."""
    return socket_type in (SocketType.SSL, SocketType.STARTTLS)


def mobileconfig_filename(domain: str) -> str:
    """Build a filesystem-safe mobileconfig filename for one domain."""
    token = re.sub(r"[^a-z0-9.-]+", "-", domain.lower()).strip("-.") or "mail"
    return f"mail-autodiscover-{token}.mobileconfig"


def apple_mail_mobileconfig(
    validated: ValidatedEmail,
    domain_settings: DomainMailSettings,
    username_format: UsernameFormat,
) -> bytes:
    """Build unsigned com.apple.mail.managed configuration profile (no passwords)."""
    username = build_username(validated, username_format)
    mail_uuid = str(
        uuid.uuid5(
            _PROFILE_NAMESPACE,
            f"{validated.email}:{domain_settings.imap.host}:{domain_settings.smtp.host}",
        )
    ).upper()
    root_uuid = str(
        uuid.uuid5(
            _PROFILE_NAMESPACE,
            f"profile:{validated.email}:{domain_settings.imap.host}",
        )
    ).upper()
    account_id = uuid.uuid5(_PROFILE_NAMESPACE, validated.email).hex
    mail_identifier = f"com.mail-autodiscover.mail.{validated.domain}.{account_id}"
    root_identifier = f"com.mail-autodiscover.profile.{validated.domain}.{account_id}"

    mail_payload: dict[str, object] = {
        "PayloadType": "com.apple.mail.managed",
        "PayloadVersion": 1,
        "PayloadIdentifier": mail_identifier,
        "PayloadUUID": mail_uuid,
        "PayloadDisplayName": f"{domain_settings.display_short_name} Mail ({validated.email})",
        "EmailAccountDescription": (
            f"{domain_settings.display_name} mail settings for {validated.email}"
        ),
        "EmailAccountName": domain_settings.display_short_name,
        "EmailAccountType": "EmailTypeIMAP",
        "EmailAddress": validated.email,
        "IncomingMailServerHostName": domain_settings.imap.host,
        "IncomingMailServerPortNumber": domain_settings.imap.port,
        "IncomingMailServerUseSSL": _use_ssl(domain_settings.imap.socket_type),
        "IncomingMailServerAuthentication": "EmailAuthPassword",
        "IncomingMailServerUsername": username,
        "OutgoingMailServerHostName": domain_settings.smtp.host,
        "OutgoingMailServerPortNumber": domain_settings.smtp.port,
        "OutgoingMailServerUseSSL": _use_ssl(domain_settings.smtp.socket_type),
        "OutgoingMailServerAuthentication": "EmailAuthPassword",
        "OutgoingMailServerUsername": username,
        "OutgoingPasswordSameAsIncomingPassword": True,
    }

    profile: dict[str, object] = {
        "PayloadType": "Configuration",
        "PayloadVersion": 1,
        "PayloadIdentifier": root_identifier,
        "PayloadUUID": root_uuid,
        "PayloadDisplayName": f"{domain_settings.display_name} ({validated.email})",
        "PayloadDescription": f"Unsigned Apple Mail profile for {validated.email}",
        "PayloadContent": [mail_payload],
    }

    return plistlib.dumps(profile, fmt=plistlib.FMT_XML)
