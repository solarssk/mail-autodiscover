# Security Policy

## Scope

**mail-autodiscover** is a lightweight HTTP service that returns IMAP/SMTP configuration XML for Outlook Autodiscover and Thunderbird Autoconfig. It is designed for self-hosted mail servers such as Synology MailPlus Server.

## Core security property: no mailbox enumeration

The service **must not** confirm whether a mailbox exists. For every syntactically valid address `@allowed-domain`, the same configuration is returned.

Do **not** add public endpoints that query Synology API, LDAP, IMAP, or a user database to verify account existence. That would enable mailbox enumeration and increase attack surface.

## Trust boundaries

```text
[Mail clients: Outlook, Thunderbird, Apple Mail (partial)]
        │ HTTPS
        ▼
[Reverse proxy — TLS termination, optional rate limiting]
        │
        ▼
[mail-autodiscover container]
```

### Public endpoints

- `GET /health`
- `GET /`
- `GET /mail/config-v1.1.xml`
- `GET /.well-known/autoconfig/mail/config-v1.1.xml`
- `POST /autodiscover/autodiscover.xml`
- `GET /autodiscover/autodiscover.xml`

There is **no admin API** in MVP. Configuration is via environment variables only.

## Data processed

| Data | Logged? | Notes |
|------|---------|-------|
| Full email addresses | **No** | Only `domain_allowed=true/false` and hashed domain prefix |
| Request XML body | **No** | Never logged |
| Client IP | Used for rate limiting | Not logged by default in access logs |
| IMAP/SMTP hosts | In XML responses | From ENV, not secret |

## Mitigations

- Safe XML parsing (`defusedxml`), body size limit
- XML output escaping
- Rate limiting per IP (`RATE_LIMIT_PER_MINUTE`)
- Security headers (`nosniff`, `no-referrer`, `DENY`, `no-store`)
- Neutral error messages (no domain list leakage)
- Non-root container user
- CI: gitleaks, bandit, pip-audit, Trivy image scan, CodeQL (GitHub default setup)

## Deployment requirements

1. Run behind HTTPS reverse proxy (nginx, Caddy, Traefik).
2. Set `TRUST_PROXY_HEADERS=true` only behind a trusted proxy.
3. Set `TRUSTED_PROXY_IPS` (or `FORWARDED_ALLOW_IPS`) to the proxy/Docker CIDRs that may set `X-Forwarded-For` / `X-Real-IP` (e.g. `127.0.0.1,172.16.2.0/24`). Empty keeps legacy behavior (trust any peer).
4. Keep `ALLOWED_DOMAINS` minimal — only domains you operate.
5. Do not expose the container directly to the internet without TLS.
6. Pull images from `ghcr.io/solarssk/autodiscover` and pin by digest or semver tag in production.

## Vulnerability disclosure

Open a **private security advisory**:

`https://github.com/solarssk/autodiscover/security/advisories/new`

Include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (optional)
