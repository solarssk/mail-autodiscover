"""Tests for Docker Compose file consistency."""

import tomllib
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "path", ["docker-compose.yml", "docker-compose.ghcr.yml", "docker-compose.dockerhub.yml"]
)
def test_compose_defaults_to_loopback_and_maps_container_port(path: str) -> None:
    content = Path(path).read_text(encoding="utf-8")
    ports_line = next(line for line in content.splitlines() if "HOST_PORT" in line)
    assert "${CONTAINER_PORT:-8000}" in ports_line
    assert ports_line.strip() == (
        '- "${HOST_BIND:-127.0.0.1}:${HOST_PORT:-8088}:${CONTAINER_PORT:-8000}"'
    )


@pytest.mark.parametrize("path", ["docker-compose.ghcr.yml", "docker-compose.dockerhub.yml"])
def test_prebuilt_compose_exposes_config_mount_and_env(path: str) -> None:
    content = Path(path).read_text(encoding="utf-8")
    assert "CONFIG_FILE: ${CONFIG_FILE:-}" in content
    assert "- ./config:/config:ro" in content
    assert 'ALLOW_INSECURE_MAIL: "${ALLOW_INSECURE_MAIL:-false}"' in content


@pytest.mark.parametrize("path", ["docker-compose.ghcr.yml", "docker-compose.dockerhub.yml"])
def test_example_image_tags_match_project_version(path: str) -> None:
    version = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"][
        "version"
    ]
    assert f"${{IMAGE_TAG:-{version}}}" in Path(path).read_text(encoding="utf-8")
    assert f"# IMAGE_TAG={version}" in Path(".env.example").read_text(encoding="utf-8")
