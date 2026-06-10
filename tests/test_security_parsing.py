"""Unit tests for safe XML parsing."""

from app.security import parse_outlook_email_address
from tests.conftest import OUTLOOK_REQUEST_TEMPLATE


def test_parse_outlook_email_address_extracts_email() -> None:
    body = OUTLOOK_REQUEST_TEMPLATE.format(email="user@example.com").encode()
    assert parse_outlook_email_address(body) == "user@example.com"


def test_parse_outlook_email_address_rejects_xxe() -> None:
    xxe = b"""<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<Autodiscover><Request><EMailAddress>&xxe;</EMailAddress></Request></Autodiscover>"""
    assert parse_outlook_email_address(xxe) is None
