"""Email validation and username formatting."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from app.config import Settings, UsernameFormat

# RFC-lite: local@domain with reasonable character sets, no wildcards
_EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)


class EmailValidationError(Enum):
    EMPTY = "empty"
    INVALID_FORMAT = "invalid_format"
    DOMAIN_NOT_ALLOWED = "domain_not_allowed"


@dataclass(frozen=True)
class ValidatedEmail:
    email: str
    domain: str
    local_part: str


def normalize_email(raw: str | None) -> str:
    if raw is None:
        return ""
    return raw.strip()


def extract_domain(email: str) -> str | None:
    if "@" not in email:
        return None
    return email.rsplit("@", 1)[1].lower()


def validate_email(
    raw: str | None, settings: Settings
) -> tuple[ValidatedEmail | None, EmailValidationError | None]:
    """Validate email syntax and domain against allowed list."""
    email = normalize_email(raw)
    if not email:
        return None, EmailValidationError.EMPTY

    if not _EMAIL_PATTERN.match(email):
        return None, EmailValidationError.INVALID_FORMAT

    domain = extract_domain(email)
    if domain is None:
        return None, EmailValidationError.INVALID_FORMAT

    if domain not in settings.allowed_domains_set:
        return None, EmailValidationError.DOMAIN_NOT_ALLOWED

    local_part = email.rsplit("@", 1)[0]
    return ValidatedEmail(email=email, domain=domain, local_part=local_part), None


def build_username(validated: ValidatedEmail, username_format: UsernameFormat) -> str:
    if username_format == UsernameFormat.LOCALPART:
        return validated.local_part
    return validated.email
