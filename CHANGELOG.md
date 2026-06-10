# Changelog

All notable changes to this project are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

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

[Unreleased]: https://github.com/solarssk/autodiscover/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/solarssk/autodiscover/releases/tag/v0.1.0
