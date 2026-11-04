# Synology Reverse Proxy

This project is designed to fit the Synology-style deployment model: one small container behind reverse proxy and then forget it.

Keep `HOST_BIND=127.0.0.1` when Synology's host reverse proxy connects to port `8088` on the same NAS. If the proxy is on another device, set a private LAN bind address and restrict access to that proxy. See the [proxy topology table](../../README.md#docker--portainer).

## Checklist

- create HTTPS reverse proxy rules for `autodiscover.` and `autoconfig.`
- send traffic to the container port from Docker Compose
- preserve the original host header
- if enabling proxy trust, add Synology / Docker bridge IP ranges to `TRUSTED_PROXY_IPS`
- overwrite or remove client-supplied `X-Real-IP` and construct `X-Forwarded-For` from the trusted connection

## Logging Warning

Synology logging may capture the full URL. Review query-string logging on Apple Mail and Thunderbird endpoints.
