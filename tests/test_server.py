"""Exercise the container's Uvicorn command across the actual TCP trust boundary."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx2
import pytest


@pytest.mark.parametrize(
    ("trust_proxy_headers", "trusted_proxy_ips", "expected"),
    [
        ("false", "127.0.0.1", [200, 429, 429]),
        ("true", "192.0.2.1", [200, 429, 429]),
        ("true", "127.0.0.1", [200, 200, 429]),
    ],
)
def test_container_startup_preserves_application_proxy_trust(
    trust_proxy_headers: str, trusted_proxy_ips: str, expected: list[int]
) -> None:
    command_line = next(
        line
        for line in Path("Dockerfile").read_text(encoding="utf-8").splitlines()
        if line.startswith("CMD ")
    )
    command = json.loads(command_line.removeprefix("CMD "))
    assert "--no-proxy-headers" in command[-1]
    assert command[-1].startswith("exec uvicorn ")
    # Bind only to loopback on the test host, not every host interface.
    command[-1] = command[-1].replace("--host 0.0.0.0", "--host 127.0.0.1")
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    environment = {
        **os.environ,
        "PATH": f"{Path(sys.executable).parent}{os.pathsep}{os.environ.get('PATH', '')}",
        "APP_ENV": "test",
        "CONFIG_FILE": "",
        "CONTAINER_PORT": str(port),
        "RATE_LIMIT_ENABLED": "true",
        "RATE_LIMIT_PER_MINUTE": "1",
        "TRUST_PROXY_HEADERS": trust_proxy_headers,
        "TRUSTED_PROXY_IPS": trusted_proxy_ips,
        # Uvicorn must ignore even this permissive value with its parsing disabled.
        "FORWARDED_ALLOW_IPS": "*",
    }
    with subprocess.Popen(
        command, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    ) as process:
        try:
            with httpx2.Client(base_url=f"http://127.0.0.1:{port}", timeout=1) as client:
                deadline = time.monotonic() + 10
                while True:
                    if process.poll() is not None:
                        pytest.fail(f"Uvicorn exited during startup: {process.communicate()}")
                    try:
                        response = client.get("/health")
                        assert response.status_code == 200
                        break
                    except httpx2.ConnectError:
                        if time.monotonic() >= deadline:
                            pytest.fail("Uvicorn did not become ready within 10 seconds")
                        time.sleep(0.05)

                statuses = [
                    client.get(
                        "/robots.txt",
                        headers={"X-Real-IP": address, "X-Forwarded-For": address},
                    ).status_code
                    for address in ["198.51.100.1", "198.51.100.2", "198.51.100.1"]
                ]
                assert statuses == expected
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
