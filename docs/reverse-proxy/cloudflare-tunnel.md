# Cloudflare Tunnel / Generic Proxy

Use this setup when the service is not directly exposed and Cloudflare or another tunnel/proxy fronts the traffic.

Run a same-host tunnel against `127.0.0.1:8088`. A tunnel in Docker should share a network and use `mail-autodiscover:8000`, not its own loopback address. For a remote connector, follow the [proxy topology table](../../README.md#docker--portainer).

## Checklist

- public hostname terminates on Cloudflare or your proxy
- proxy forwards requests to the service over a trusted private path
- `PUBLIC_BASE_URL` still points at the public HTTPS hostname
- if you enable proxy trust, include the direct peer addresses that connect to the app
- overwrite or remove client-supplied `X-Real-IP`; do not assume trusting the tunnel peer validates every header it forwards

## Logging Warning

Cloudflare and similar products may log full URLs, including `emailaddress=` query values.
