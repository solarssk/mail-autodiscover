"""Tests for release notes formatting."""

from scripts.format_release_notes import build_release_notes


def test_build_release_notes_v0_1_1() -> None:
    notes = build_release_notes("0.1.1")
    assert "## 🚀 mail-autodiscover v0.1.1" in notes
    assert "## What's new" in notes
    assert "## What this means" in notes
    assert "## Action required" in notes
    assert "- No action required." in notes
    assert "## Technical details" in notes
    assert "### 🔄 Changed" in notes
    assert "actions/checkout" in notes
    assert "## 🐳 Docker" in notes
    assert "ghcr.io/solarssk/autodiscover:0.1.1" in notes
    assert "## 📚 Links" in notes


def test_build_release_notes_v0_1_0() -> None:
    notes = build_release_notes("0.1.0")
    assert "### ✨ Added" in notes
    assert "Outlook Autodiscover" in notes
    assert "Configure your environment variables" in notes


def test_build_release_notes_v0_2_0_has_admin_action() -> None:
    notes = build_release_notes("0.2.0")
    assert "## Action required" in notes
    assert "review and set `TRUSTED_PROXY_IPS`" in notes
    assert "### 🔒 Security" in notes
