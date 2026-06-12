# Nginx Proxy Manager

Create a proxy host for your autodiscovery hostname and point it at the container port.

## Checklist

- enable SSL
- forward the original host
- ensure `X-Forwarded-For` and `X-Real-IP` reach the app if you use proxy trust
- do not pass through client-supplied `X-Forwarded-For` unchanged; see [nginx.md](nginx.md) for the safe header pattern
- point both `autodiscover.` and `autoconfig.` records to the proxy

## Logging Warning

NPM can log full request URIs. Review logging for autoconfig paths because they contain `emailaddress=`.
