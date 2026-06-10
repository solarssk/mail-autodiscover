#!/usr/bin/env python3
"""Format CHANGELOG section into GitHub Release notes with emoji sections."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SECTION_EMOJI = {
    "added": "✨ Added",
    "changed": "🔄 Changed",
    "deprecated": "⚠️ Deprecated",
    "removed": "🗑️ Removed",
    "fixed": "🐛 Fixed",
    "security": "🔒 Security",
    "note": "📝 Note",
}

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"
IMAGE = "ghcr.io/solarssk/autodiscover"


def parse_version(tag: str) -> str:
    return tag.removeprefix("v")


def extract_section(changelog: str, version: str) -> str:
    pattern = rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|\Z)"
    match = re.search(pattern, changelog, flags=re.MULTILINE | re.DOTALL)
    if not match:
        msg = f"No CHANGELOG section found for version {version}"
        raise SystemExit(msg)
    return match.group(1).strip()


def format_subsections(body: str) -> str:
    lines: list[str] = []
    current_heading: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal current_heading, buffer
        if current_heading is None:
            return
        emoji_heading = SECTION_EMOJI.get(current_heading.lower(), f"📌 {current_heading}")
        lines.append(f"### {emoji_heading}")
        lines.extend(buffer)
        lines.append("")
        current_heading = None
        buffer = []

    for raw in body.splitlines():
        line = raw.rstrip()
        if line.startswith("### "):
            flush()
            current_heading = line.removeprefix("### ").strip()
            continue
        if current_heading is not None:
            buffer.append(line)

    flush()
    return "\n".join(lines).strip()


def docker_block(version: str, prerelease: bool) -> str:
    tag = version
    lines = [
        "---",
        "",
        "## 🐳 Docker",
        "",
        "```text",
        f"{IMAGE}:{tag}",
        f"{IMAGE}:{tag.rsplit('.', 1)[0]}" if "." in tag else f"{IMAGE}:{tag}",
    ]
    if not prerelease and "-" not in tag:
        lines.append(f"{IMAGE}:latest")
    lines.extend(
        [
            "```",
            "",
            "**Portainer / production:** pin the semver tag, not `latest`.",
            "",
            "## 📚 Links",
            "",
            "- [Full CHANGELOG](https://github.com/solarssk/autodiscover/blob/main/CHANGELOG.md)",
            "- [README](https://github.com/solarssk/autodiscover#portainer--ghcr-recommended)",
            "- [.env.example](https://github.com/solarssk/autodiscover/blob/main/.env.example)",
        ]
    )
    return "\n".join(lines)


def build_release_notes(version: str, prerelease: bool = False) -> str:
    changelog = CHANGELOG.read_text(encoding="utf-8")
    body = extract_section(changelog, version)
    formatted = format_subsections(body)

    header = f"## 🚀 mail-autodiscover v{version}"
    if prerelease:
        header += " (pre-release)"

    parts = [header, "", formatted, "", docker_block(version, prerelease)]
    return "\n".join(parts).strip() + "\n"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: format_release_notes.py <tag>   e.g. v0.1.1")

    tag = sys.argv[1]
    version = parse_version(tag)
    prerelease = "-" in version
    sys.stdout.write(build_release_notes(version, prerelease=prerelease))


if __name__ == "__main__":
    main()
