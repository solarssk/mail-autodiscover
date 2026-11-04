# Nginx Proxy Manager

Create a proxy host for your autodiscovery hostname and point it at the container port.

If NPM runs in Docker, join a shared network and use `mail-autodiscover:8000`. A published loopback port is not reachable as `127.0.0.1` from another container. For remote NPM, follow the [proxy topology table](../../README.md#docker--portainer).

## Checklist

- enable SSL
- forward the original host
- ensure `X-Forwarded-For` and `X-Real-IP` reach the app if you use proxy trust
- do not pass through client-supplied `X-Forwarded-For` unchanged; see [nginx.md](nginx.md) for the safe header pattern
- overwrite client-supplied `X-Real-IP` too
- point both `autodiscover.` and `autoconfig.` records to the proxy

## Logging Warning

NPM can log full request URIs. Review logging for autoconfig paths because they contain `emailaddress=`.
