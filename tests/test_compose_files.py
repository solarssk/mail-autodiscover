"""Tests for Docker Compose file consistency."""

from pathlib import Path


def test_ghcr_compose_maps_container_port() -> None:
    content = Path("docker-compose.ghcr.yml").read_text(encoding="utf-8")
    ports_line = next(line for line in content.splitlines() if "HOST_PORT" in line)
    assert "${CONTAINER_PORT:-8000}" in ports_line
    assert ports_line.strip() == '- "${HOST_PORT:-8088}:${CONTAINER_PORT:-8000}"'
