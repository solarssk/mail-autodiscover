# Security Policy

This document is for maintainers and admins who need the detailed security model behind `mail-autodiscover`.

If you are looking for setup help, start with [`README.md`](README.md) and the wiki pages in [`wiki/`](wiki/).

## What this service is allowed to do

`mail-autodiscover` may return mail client configuration for allowed domains.

It may not:

- verify that a mailbox exists,
- expose internal domain lists on the public landing page,
- act as an admin panel,
- connect to LDAP, IMAP, Synology APIs, or user databases to validate an email address.

Those limits are intentional. They keep the service small and reduce the risk of mailbox enumeration.

## Core security property: no mailbox enumeration

For every syntactically valid address in an allowed domain, the service returns the same configuration shape.

That means the service must not reveal whether `alice@example.com` exists while `bob@example.com` does not. Any future feature that checks mailbox existence would break the project's main security guarantee.

## Trust boundaries

```text
[Mail clients: Outlook, Thunderbird, Apple Mail]
        │ HTTPS
        ▼
[Reverse proxy: TLS termination, optional rate limiting]
        │
        ▼
[mail-autodiscover container]
```

## Public endpoints

- `GET /health`
- `GET /`
- `GET /robots.txt`
- `GET /favicon.ico`
- `GET /apple-touch-icon.png`
- `GET /mail/config-v1.1.xml`
- `GET /.well-known/autoconfig/mail/config-v1.1.xml`
- `GET /mail/ios.mobileconfig`
- `GET /.well-known/apple-mail.mobileconfig`
- `POST /autodiscover/autodiscover.xml`
- `GET /autodiscover/autodiscover.xml`

There is no admin API in the current version. All configuration is supplied through environment variables.

## Data handling

| Data | Logged? | Notes |
|------|---------|-------|
| Full email addresses | No | Logs include only `domain_allowed=true/false` and a hashed domain prefix |
| Request XML body | No | Request bodies are never logged |
| Client IP | Yes | Stored in the unified access log as `client_ip=` |
| IMAP/SMTP hosts | Returned to clients | Comes from environment variables, not from a user database |

## Built-in mitigations

- Safe XML parsing with `defusedxml`
- Request body size limit
- XML output escaping
- Rate limiting per IP with `RATE_LIMIT_PER_MINUTE`
- Security headers such as `nosniff`, `no-referrer`, `DENY`, and `no-store`
- Neutral error responses that do not expose your domain list
- Non-root container user
- CI security checks with `gitleaks`, `bandit`, `pip-audit`, Trivy, and CodeQL

## Deployment requirements

1. Run the service behind an HTTPS reverse proxy.
2. Enable `TRUST_PROXY_HEADERS=true` only when requests really come through a trusted proxy.
3. Set `TRUSTED_PROXY_IPS` or `FORWARDED_ALLOW_IPS` to your own proxy or Docker bridge CIDRs.
4. Keep `ALLOWED_DOMAINS` limited to domains you actually operate.
5. Do not expose the container directly to the public internet without TLS.
6. In production, pin GHCR images by semver tag or digest instead of using `latest`.

## What not to add casually

Changes in the list below need a deliberate security review because they would alter the trust model:

- mailbox existence checks,
- public endpoints that query LDAP, IMAP, or Synology APIs,
- user-specific routing logic,
- a public page that exposes internal hostnames or allowed domains,
- forwarded-header trust without explicit proxy restrictions.

## Vulnerability disclosure

Please open a private security advisory instead of a public issue:

[Create a private advisory](https://github.com/solarssk/autodiscover/security/advisories/new)

Include:

- a short description of the issue,
- steps to reproduce,
- expected impact,
- an optional suggested fix.
