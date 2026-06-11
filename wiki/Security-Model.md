# Security Model

The short version: this project is intentionally narrow.

Its job is to return mail client settings. Its job is not to prove that a mailbox exists.

## Security priorities

1. Do not leak mailbox existence.
2. Do not log full email addresses.
3. Do not trust forwarded headers from arbitrary sources.
4. Keep public responses small and predictable.

## Design choices that support those priorities

- same response shape for valid addresses in allowed domains,
- no LDAP, IMAP, or Synology lookups,
- safe XML parsing,
- rate limiting,
- security headers,
- no admin panel.

## Operational expectations

You still need to deploy it correctly:

- behind HTTPS,
- with trusted proxy IPs defined,
- with minimal allowed domains,
- with production image tags pinned.

For the maintainer-level policy, see [`SECURITY.md`](../SECURITY.md).
