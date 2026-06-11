"""Security middleware: rate limiting, headers, safe logging."""

from __future__ import annotations

import hashlib
import ipaddress
import logging
import time
import uuid
from collections import defaultdict
from collections.abc import Awaitable, Callable
from threading import Lock

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import Settings

logger = logging.getLogger("mail_autodiscover.access")

_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_rate_limit_lock = Lock()


def _peer_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None


def _ip_in_trusted_networks(
    ip_str: str,
    networks: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...],
) -> bool:
    """Return whether an IP address falls within any configured proxy network."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return any(ip in network for network in networks)


def _should_trust_forwarded_headers(request: Request, settings: Settings) -> bool:
    """Decide if X-Forwarded-For may be used based on proxy trust settings."""
    if not settings.trust_proxy_headers:
        return False
    networks = settings.trusted_proxy_networks
    if not networks:
        return True
    peer = _peer_ip(request)
    if peer is None:
        return False
    return _ip_in_trusted_networks(peer, networks)


def get_client_ip(request: Request, settings: Settings) -> str:
    """Resolve client IP, honoring forwarded headers only from trusted proxies."""
    if _should_trust_forwarded_headers(request, settings):
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
    peer = _peer_ip(request)
    if peer:
        return peer
    return "unknown"


def hash_domain(domain: str) -> str:
    """Return a short stable hash of a domain for privacy-safe access logs."""
    return hashlib.sha256(domain.encode()).hexdigest()[:12]


def should_skip_rate_limit(path: str) -> bool:
    """Return whether the path is exempt from per-IP rate limiting."""
    return path == "/health"


def should_skip_access_log(path: str, settings: Settings) -> bool:
    """Return whether the path should be omitted from access logs."""
    return path in settings.access_log_skip_paths_set


def is_rate_limited(client_ip: str, settings: Settings) -> bool:
    """Track request timestamps per IP and report when the minute window is exceeded."""
    if not settings.rate_limit_enabled:
        return False

    now = time.monotonic()
    window = 60.0
    limit = settings.rate_limit_per_minute

    with _rate_limit_lock:
        timestamps = _rate_limit_store[client_ip]
        _rate_limit_store[client_ip] = [t for t in timestamps if now - t < window]
        if len(_rate_limit_store[client_ip]) >= limit:
            return True
        _rate_limit_store[client_ip].append(now)
    return False


def reset_rate_limit_store() -> None:
    """Clear in-memory rate limit state (for tests)."""
    with _rate_limit_lock:
        _rate_limit_store.clear()


class SecurityMiddleware(BaseHTTPMiddleware):
    """Apply rate limits, security headers, and privacy-safe access logging."""

    def __init__(self, app: object, settings: Settings) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self.settings = settings

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Enforce limits, attach headers, and log requests without full email addresses."""
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        request.state.request_id = request_id
        request.state.domain_allowed = None

        path = request.url.path
        client_ip = get_client_ip(request, self.settings)
        if not should_skip_rate_limit(path) and is_rate_limited(client_ip, self.settings):
            logger.warning(
                "request_id=%s endpoint=%s status=429 rate_limited=true",
                request_id,
                request.url.path,
            )
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"X-Request-ID": request_id},
            )

        response = await call_next(request)

        if self.settings.security_headers_enabled:
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Cache-Control"] = "no-store"

        response.headers["X-Request-ID"] = request_id

        if not self.settings.disable_access_log and not should_skip_access_log(
            path, self.settings
        ):
            domain_allowed = getattr(request.state, "domain_allowed", None)
            if domain_allowed is None:
                domain_info = "domain_allowed=unknown"
            else:
                domain_info = f"domain_allowed={'true' if domain_allowed else 'false'}"
            domain_hash = getattr(request.state, "domain_hash", None)
            if domain_hash:
                domain_info += f" domain_hash={domain_hash}"

            logger.info(
                "request_id=%s client_ip=%s method=%s endpoint=%s status=%s %s",
                request_id,
                client_ip,
                request.method,
                path,
                response.status_code,
                domain_info,
            )

        return response


def parse_outlook_email_address(body: bytes) -> str | None:
    """Safely parse Outlook autodiscover request XML and extract EMailAddress."""
    from defusedxml.ElementTree import fromstring  # type: ignore[import-untyped]

    try:
        root = fromstring(body)
    except Exception:
        return None

    for elem in root.iter():
        local_tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        if local_tag == "EMailAddress" and elem.text:
            return str(elem.text.strip())
    return None
