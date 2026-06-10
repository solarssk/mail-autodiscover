# Changelog

All notable changes to this project are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [0.1.2] - 2026-06-10

### Security

- Harden Docker image: `python:3.12-slim-bookworm`, `apt-get upgrade`, pip ≥ 26.1.2
- Fix CodeQL `py/incomplete-url-substring-sanitization` alerts in tests (assert XML elements instead of hostname substrings)

### Note

- CodeQL runs via GitHub default setup (no custom workflow)

## [0.1.1] - 2026-06-10

### Changed

- Bump `actions/checkout` to v6.0.3
- Bump `gitleaks/gitleaks-action` (merged via dependabot)

### Note

- Declined Python 3.14 Docker base image bump (stay on 3.12-slim for CI/runtime parity)

## [0.1.0] - 2026-06-10

### Added

- Outlook Autodiscover (`POST /autodiscover/autodiscover.xml`)
- Thunderbird Autoconfig (`GET /mail/config-v1.1.xml`)
- ENV-based configuration via pydantic-settings
- Docker and Docker Compose support
- Security middleware (rate limit, headers, safe logging)
- pytest test suite (50 tests, ≥90% coverage)
- Hardened CI (gitleaks, ruff, mypy, bandit, pip-audit, deptry, Trivy)
- GHCR image publishing (`ghcr.io/solarssk/autodiscover`)
- CONTRIBUTING, SECURITY, issue/PR templates, Dependabot
- Branch protection and repository labels
- MIT license

[Unreleased]: https://github.com/solarssk/autodiscover/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/solarssk/autodiscover/releases/tag/v0.1.2
[0.1.1]: https://github.com/solarssk/autodiscover/compare/v0.1.1...v0.1.2
[0.1.0]: https://github.com/solarssk/autodiscover/releases/tag/v0.1.0
