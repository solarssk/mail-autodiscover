"""Security middleware: rate limiting, headers, safe logging."""

from __future__ import annotations

import hashlib
import ipaddress
import json
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
_last_rate_limit_cleanup = 0.0


def _log_event(
    level: int,
    *,
    json_mode: bool,
    logger_name: logging.Logger,
    **fields: object,
) -> None:
    """Log access events as structured JSON or compact key=value pairs."""
    if json_mode:
        logger_name.log(level, json.dumps(fields, sort_keys=True, separators=(",", ":")))
        return
    message = " ".join(f"{key}={value}" for key, value in fields.items())
    logger_name.log(level, message)


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


def _parse_ip(value: str) -> str | None:
    """Return a normalized IP string when value is a valid address."""
    try:
        return str(ipaddress.ip_address(value.strip()))
    except ValueError:
        return None


def _should_trust_forwarded_headers(request: Request, settings: Settings) -> bool:
    """Decide if forwarded client IP headers may be used based on proxy trust settings."""
    if not settings.trust_proxy_headers:
        return False
    networks = settings.trusted_proxy_networks
    if not networks:
        return False
    peer = _peer_ip(request)
    if peer is None:
        return False
    return _ip_in_trusted_networks(peer, networks)


def _client_ip_from_forwarded_for(
    forwarded: str,
    networks: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...],
) -> str | None:
    """Parse X-Forwarded-For right-to-left, skipping trusted proxy hops."""
    parsed_ips: list[str] = []
    for part in forwarded.split(","):
        token = part.strip()
        if not token:
            continue
        parsed = _parse_ip(token)
        if parsed is None:
            continue
        parsed_ips.append(parsed)

    for parsed in reversed(parsed_ips):
        if not _ip_in_trusted_networks(parsed, networks):
            return parsed

    if parsed_ips:
        return parsed_ips[0]
    return None


def get_client_ip(request: Request, settings: Settings) -> str:
    """Resolve client IP, honoring forwarded headers only from trusted proxies."""
    peer = _peer_ip(request)
    if _should_trust_forwarded_headers(request, settings):
        networks = settings.trusted_proxy_networks
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            parsed = _parse_ip(real_ip)
            if parsed is not None and not _ip_in_trusted_networks(parsed, networks):
                return parsed
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            parsed = _client_ip_from_forwarded_for(forwarded, networks)
            if parsed is not None:
                return parsed
    if peer:
        return peer
    return "unknown"


def _cleanup_rate_limit_store(now: float, settings: Settings) -> None:
    """Remove stale client entries and evict oldest keys when over capacity."""
    global _last_rate_limit_cleanup

    window = 60.0
    interval = float(settings.rate_limit_cleanup_interval_seconds)
    if now - _last_rate_limit_cleanup >= interval:
        _last_rate_limit_cleanup = now
        stale_keys = [
            ip
            for ip, timestamps in _rate_limit_store.items()
            if not timestamps or now - timestamps[-1] >= window
        ]
        for ip in stale_keys:
            del _rate_limit_store[ip]

def _enforce_rate_limit_capacity(settings: Settings) -> None:
    """Evict oldest client entries when the store exceeds configured capacity."""
    max_clients = settings.rate_limit_max_clients
    if len(_rate_limit_store) <= max_clients:
        return

    ranked = sorted(
        _rate_limit_store.items(),
        key=lambda item: item[1][-1] if item[1] else 0.0,
    )
    for ip, _ in ranked[: len(_rate_limit_store) - max_clients]:
        del _rate_limit_store[ip]


def hash_domain(domain: str) -> str:
    """Return a short stable hash of a domain for privacy-safe access logs."""
    return hashlib.sha256(domain.encode()).hexdigest()[:12]


def should_skip_rate_limit(path: str) -> bool:
    """Return whether the path is exempt from per-IP rate limiting."""
    return path in {"/health", "/ready"}


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
        _cleanup_rate_limit_store(now, settings)
        timestamps = _rate_limit_store[client_ip]
        _rate_limit_store[client_ip] = [t for t in timestamps if now - t < window]
        if len(_rate_limit_store[client_ip]) >= limit:
            return True
        _rate_limit_store[client_ip].append(now)
        _enforce_rate_limit_capacity(settings)
    return False


def reset_rate_limit_store() -> None:
    """Clear in-memory rate limit state (for tests)."""
    global _last_rate_limit_cleanup
    with _rate_limit_lock:
        _rate_limit_store.clear()
        _last_rate_limit_cleanup = 0.0


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
            _log_event(
                logging.WARNING,
                json_mode=self.settings.structured_json_logs,
                logger_name=logger,
                event="request",
                request_id=request_id,
                endpoint=request.url.path,
                status=429,
                rate_limited=True,
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
                if self.settings.structured_json_logs:
                    _log_event(
                        logging.INFO,
                        json_mode=True,
                        logger_name=logger,
                        event="request",
                        request_id=request_id,
                        client_ip=client_ip,
                        method=request.method,
                        endpoint=path,
                        status=response.status_code,
                        domain_allowed=domain_allowed,
                        domain_hash=domain_hash,
                    )
                else:
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
            else:
                _log_event(
                    logging.INFO,
                    json_mode=self.settings.structured_json_logs,
                    logger_name=logger,
                    event="request",
                    request_id=request_id,
                    client_ip=client_ip,
                    method=request.method,
                    endpoint=path,
                    status=response.status_code,
                    domain_allowed=domain_allowed,
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
