"""Unit tests for XML template generators."""

from app.config import UsernameFormat
from app.email_utils import ValidatedEmail, build_username
from app.templates import outlook_autodiscover, thunderbird_autoconfig
from tests.conftest import make_settings


def test_outlook_template_escapes_login_name() -> None:
    settings = make_settings()
    validated = ValidatedEmail(
        email="user<script>@example.com",
        domain="example.com",
        local_part="user<script>",
    )
    xml = outlook_autodiscover(validated, settings)
    assert "user&lt;script&gt;@example.com" in xml
    assert "<script>" not in xml


def test_thunderbird_template_localpart_username() -> None:
    settings = make_settings(username_format=UsernameFormat.LOCALPART)
    validated = ValidatedEmail(
        email="jan@example.com",
        domain="example.com",
        local_part="jan",
    )
    username = build_username(validated, settings.username_format)
    xml = thunderbird_autoconfig(validated, settings)
    assert f"<username>{username}</username>" in xml
    assert "<username>jan</username>" in xml
