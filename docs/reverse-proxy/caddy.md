# Caddy

Point your public mail autodiscovery hostnames at Caddy and reverse proxy them to the container.

Use `127.0.0.1:8088` for a same-host Caddy process. For containerized or remote Caddy, follow the [proxy topology table](../../README.md#docker--portainer).

## Requirements

- serve HTTPS publicly
- preserve `Host`
- pass client IP headers if you enable trusted proxy handling in the app

For a single-hop proxy, construct `X-Forwarded-For` from the connecting client's IP. Remove client-supplied `X-Real-IP` or overwrite it with that same IP; Caddy forwarding an arbitrary `X-Real-IP` is not sufficient. The application prefers `X-Real-IP` when present.

## Logging Warning

Thunderbird and Apple Mail requests include mailbox addresses in the query string. Configure access logs accordingly if you do not want those URIs stored.

## Test

```bash
curl -I https://autoconfig.example.com/mail/config-v1.1.xml?emailaddress=user@example.com
```
