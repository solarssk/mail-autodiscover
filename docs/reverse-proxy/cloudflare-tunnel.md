# Cloudflare Tunnel / Generic Proxy

Use this setup when the service is not directly exposed and Cloudflare or another tunnel/proxy fronts the traffic.

## Checklist

- public hostname terminates on Cloudflare or your proxy
- proxy forwards requests to the service over a trusted private path
- `PUBLIC_BASE_URL` still points at the public HTTPS hostname
- if you enable proxy trust, include the direct peer addresses that connect to the app

## Logging Warning

Cloudflare and similar products may log full URLs, including `emailaddress=` query values.
