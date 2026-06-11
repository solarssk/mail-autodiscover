# Caddy

Point your public mail autodiscovery hostnames at Caddy and reverse proxy them to the container.

## Requirements

- serve HTTPS publicly
- preserve `Host`
- pass client IP headers if you enable trusted proxy handling in the app

## Logging Warning

Thunderbird and Apple Mail requests include mailbox addresses in the query string. Configure access logs accordingly if you do not want those URIs stored.

## Test

```bash
curl -I https://autoconfig.example.com/mail/config-v1.1.xml?emailaddress=user@example.com
```
