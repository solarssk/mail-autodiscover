# Changelog

All notable changes to this project are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [0.2.2] - 2026-06-12

### What's new

- Production deployments now fail fast on unsafe placeholder configuration instead of starting with `example.com` defaults.
- Reverse-proxy trust is safer by default: forwarded headers require explicit trusted proxy CIDRs.

### What this means

- Misconfigured production stacks surface a clear startup error instead of silently serving placeholder mail settings.
- Rate limiting uses a bounded in-memory store with periodic cleanup, reducing memory growth under abuse.

### Action required

- If you run behind a reverse proxy with `TRUST_PROXY_HEADERS=true`, set `TRUSTED_PROXY_IPS` to your proxy or Docker bridge CIDRs before upgrading to `0.2.2` in production.
- Review reverse-proxy access logs: Thunderbird and Apple Mail endpoints pass `emailaddress` in the query string.

### Security

- Default `TRUST_PROXY_HEADERS` changed to `false`; empty `TRUSTED_PROXY_IPS` no longer trusts all peers.
- `X-Forwarded-For` and `X-Real-IP` values are validated as real IP addresses before use.
- Production startup validation for HTTPS `PUBLIC_BASE_URL`, real domains, and proxy trust settings.

### Added

- `RATE_LIMIT_MAX_CLIENTS` and `RATE_LIMIT_CLEANUP_INTERVAL_SECONDS` for bounded rate-limit storage.
- Stable UUIDv5 identifiers in Apple `.mobileconfig` profiles (re-download updates the same profile).
- Healthcheck in `docker-compose.ghcr.yml`.

### Changed

- `TRUST_PROXY_HEADERS` default is now `false` in application config, `.env.example`, and GHCR compose.
- Trivy blocks CRITICAL vulnerabilities on pull requests; `main` keeps advisory SARIF upload.

### Fixed

- `docker-compose.ghcr.yml` port mapping now respects `CONTAINER_PORT`.
- Apple `.mobileconfig` `PayloadIdentifier` values are account-specific so multiple mailboxes on one domain do not collide.
- `docker-compose.ghcr.yml` default `IMAGE_TAG` matches the release version (`0.2.2`).

## [0.2.1] - 2026-06-11

### What's new

- The project now lives at `mail-autodiscover`, with GHCR images published only under `ghcr.io/solarssk/mail-autodiscover`.
- Documentation moved to the GitHub Wiki, and the public Python API is now documented with module docstrings.

### What this means

- New installs have one canonical repository and container image name.
- Admins follow wiki links from the README instead of the removed in-repo `wiki/` folder.

### Action required

- Pull `ghcr.io/solarssk/mail-autodiscover` instead of the retired `ghcr.io/solarssk/autodiscover` package path.
- Pin `IMAGE_TAG=0.2.1` (or newer) in production rather than the old `autodiscover` image tags.

### Changed

- GitHub repository renamed to `mail-autodiscover`; GHCR images publish as `ghcr.io/solarssk/mail-autodiscover`
- Documentation now links to the GitHub Wiki instead of the in-repo `wiki/` folder
- Replace flaky GitHub CodeQL default setup with explicit `.github/workflows/codeql.yml`
- Add docstrings across the `app/` package for public API and security helpers

## [0.2.0] - 2026-06-10

### What's new

- This release makes reverse-proxy deployments safer, adds a simple landing page, and introduces Apple Mail profile downloads.

### What this means

- Admins get clearer logging, better control over forwarded headers, and a cleaner user-facing entry point.
- End users on iPhone, iPad, and Mac can install a mail profile instead of entering all settings by hand.

### Action required

- If you run the service behind a reverse proxy, review and set `TRUSTED_PROXY_IPS` for your own proxy or Docker network ranges.
- If you deploy with Portainer or GHCR images, prefer the pinned `0.2.0` tag in production.

### Added

- `TRUSTED_PROXY_IPS` / `FORWARDED_ALLOW_IPS` so forwarded client IP headers are trusted only from your configured proxy CIDRs
- `ACCESS_LOG_SKIP_PATHS` to reduce noise from health checks and static asset requests
- Apple Mail `.mobileconfig` profiles (`GET /mail/ios.mobileconfig`, `/.well-known/apple-mail.mobileconfig`)
- HTML landing page, `robots.txt`, `favicon.ico`, `apple-touch-icon.png`
- `docker-compose.ghcr.yml` example for Portainer / GHCR deployments

### Changed

- Unified access logs now show `client_ip`, method, endpoint, and status in a single line
- `GET /` now returns a small landing page instead of JSON metadata
- `/health` is no longer rate limited

### Security

- Forwarded headers are honored only when the direct peer matches `TRUSTED_PROXY_IPS` when that setting is present

## [0.1.2] - 2026-06-10

### What's new

- This is a maintenance and hardening release focused on container safety and CI security checks.

### What this means

- Runtime behavior stays the same, but the delivery pipeline and base image are more defensive.

### Action required

- No action required.

### Security

- Docker image hardening: `python:3.12-slim-bookworm`, `apt-get upgrade`, pip >= `26.1.2`
- CodeQL-related test adjustments to avoid unsafe URL substring assertions

### Note

- CodeQL ran via GitHub default setup in this release

## [0.1.1] - 2026-06-10

### What's new

- This is a dependency and CI maintenance release.

### What this means

- There are no product-level changes for admins or end users, only safer and cleaner project maintenance.

### Action required

- No action required.

### Changed

- Bump `actions/checkout` to `v6.0.3`
- Bump `gitleaks/gitleaks-action` through Dependabot

### Note

- Python `3.14` Docker base image bump was intentionally declined to keep CI and runtime aligned on `3.12`

## [0.1.0] - 2026-06-10

### What's new

- First public release of `mail-autodiscover` with Outlook and Thunderbird support, Docker packaging, and baseline security controls.

### What this means

- Self-hosted mail admins can expose standards-based autodiscovery without building a custom service.
- The service is ready for simple production deployments where one domain or a small set of domains share the same mail settings.

### Action required

- Configure your environment variables, deploy behind HTTPS, and create the required DNS records before pointing users to the service.

### Added

- Outlook Autodiscover (`POST /autodiscover/autodiscover.xml`)
- Thunderbird Autoconfig (`GET /mail/config-v1.1.xml`)
- Environment-based configuration via `pydantic-settings`
- Docker and Docker Compose support
- Security middleware for rate limiting, headers, and safe logging
- `pytest` test suite with coverage gate
- Hardened CI with `gitleaks`, `ruff`, `mypy`, `bandit`, `pip-audit`, `deptry`, and Trivy
- GHCR image publishing (`ghcr.io/solarssk/mail-autodiscover`)
- `CONTRIBUTING.md`, `SECURITY.md`, issue templates, PR template, and Dependabot
- Branch protection and repository labels
- MIT license

[Unreleased]: https://github.com/solarssk/mail-autodiscover/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/solarssk/mail-autodiscover/releases/tag/v0.2.1
[0.2.0]: https://github.com/solarssk/mail-autodiscover/compare/v0.2.0...v0.2.1
[0.1.2]: https://github.com/solarssk/mail-autodiscover/compare/v0.1.2...v0.2.0
[0.1.1]: https://github.com/solarssk/mail-autodiscover/compare/v0.1.1...v0.1.2
[0.1.0]: https://github.com/solarssk/mail-autodiscover/releases/tag/v0.1.0
