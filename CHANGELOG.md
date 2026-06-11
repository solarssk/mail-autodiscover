# Changelog

All notable changes to this project are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### What's new

- Release automation now uses the repository CodeQL workflow instead of GitHub's default setup.

### What this means

- Security scanning is configured in-repo and easier to review alongside the rest of the CI configuration.

### Action required

- New deployments should pull `ghcr.io/solarssk/mail-autodiscover` instead of the old `autodiscover` package path.
- Pin `IMAGE_TAG` to a semver tag in production; compose defaults to `latest` until you choose a release tag.

### Changed

- GitHub repository renamed to `mail-autodiscover`; GHCR images publish as `ghcr.io/solarssk/mail-autodiscover`
- Documentation now links to the GitHub Wiki instead of the in-repo `wiki/` folder
- Replace flaky GitHub CodeQL default setup with explicit `.github/workflows/codeql.yml`

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

[Unreleased]: https://github.com/solarssk/mail-autodiscover/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/solarssk/mail-autodiscover/releases/tag/v0.2.0
[0.1.2]: https://github.com/solarssk/mail-autodiscover/compare/v0.1.2...v0.2.0
[0.1.1]: https://github.com/solarssk/mail-autodiscover/compare/v0.1.1...v0.1.2
[0.1.0]: https://github.com/solarssk/mail-autodiscover/releases/tag/v0.1.0
