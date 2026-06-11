# Synology Reverse Proxy

This project is designed to fit the Synology-style deployment model: one small container behind reverse proxy and then forget it.

## Checklist

- create HTTPS reverse proxy rules for `autodiscover.` and `autoconfig.`
- send traffic to the container port from Docker Compose
- preserve the original host header
- if enabling proxy trust, add Synology / Docker bridge IP ranges to `TRUSTED_PROXY_IPS`

## Logging Warning

Synology logging may capture the full URL. Review query-string logging on Apple Mail and Thunderbird endpoints.
