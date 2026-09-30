# Endpoint Reference

Every route the service exposes: what it takes, what it returns, and which status codes it can answer with.

The service is stateless and never checks whether a mailbox exists (see [SECURITY.md](../SECURITY.md)), so a syntactically valid address in an allowed domain gets the same answer whether or not the mailbox is real. The interactive API docs are switched off (`/docs`, `/redoc` and `/openapi.json` do not exist), so this page is the reference.

## Routes

| Method | Path | Input | Success response |
|--------|------|-------|------------------|
| `GET` | `/health` | none | `200`, `application/json`: `{"status":"ok"}` |
| `GET` | `/ready` | none | `200`, `application/json`: `{"status":"ready"}` |
| `GET` | `/` | none | `200`, `text/html`: minimal landing page |
| `GET` | `/robots.txt` | none | `200`, `text/plain`: no-index hint |
| `GET` | `/favicon.ico` | none | `200`, `image/x-icon` |
| `GET` | `/apple-touch-icon.png` | none | `200`, `image/png` |
| `GET` | `/mail/config-v1.1.xml`<br>`/.well-known/autoconfig/mail/config-v1.1.xml` | query `emailaddress` | `200`, `application/xml`: Thunderbird `clientConfig` 1.1 |
| `GET` | `/mail/ios.mobileconfig`<br>`/.well-known/apple-mail.mobileconfig` | query `emailaddress` | `200`, `application/x-apple-aspen-config`, sent as an attachment named `mail-autodiscover-<domain>.mobileconfig` |
| `POST` | `/autodiscover/autodiscover.xml` | XML body containing an `EMailAddress` element | `200`, `application/xml`: Outlook Autodiscover response |
| `GET` | `/autodiscover/autodiscover.xml` | none | `200`, `application/xml`: neutral Outlook error (`Code="600"`), the same for everyone, also when `OUTLOOK_ENABLED=false` |

The two Thunderbird paths and the two Apple Mail paths are aliases and answer identically. Every response carries an `X-Request-ID` header. It also carries the security headers described in [SECURITY.md](../SECURITY.md) unless you set `SECURITY_HEADERS_ENABLED=false` (they are on by default).

## Status Codes

Error bodies are always JSON, `{"detail": "..."}`.

| Status | Body `detail` | When |
|--------|---------------|------|
| `200` | none (XML, profile or JSON as above) | Address is in an allowed domain and the protocol is enabled |
| `400` | `Invalid request` | Thunderbird / Apple Mail: `emailaddress` missing or empty. Outlook: body is not parseable XML, has no `EMailAddress`, or the address is not syntactically valid |
| `400` | `Configuration not available` | Where the table below would return `404 Not found` for an unknown domain (or a malformed address on a Thunderbird / Apple Mail route), but `RETURN_404_FOR_UNKNOWN_DOMAIN=false` is set |
| `404` | `Not found` | Address is not in an allowed domain (default), a malformed address on a Thunderbird / Apple Mail route, or the protocol is switched off: `THUNDERBIRD_ENABLED=false` or `APPLE_MOBILECONFIG_ENABLED=false` for their routes, `OUTLOOK_ENABLED=false` for `POST /autodiscover/autodiscover.xml` only |
| `404` | `Not Found` | Any path that is not listed above |
| `405` | `Method Not Allowed` | A listed path used with the wrong HTTP method |
| `413` | `Request entity too large` | Outlook `POST` body is larger than `MAX_REQUEST_BODY_BYTES` (default `16384`) |
| `429` | `Too many requests` | Rate limiting is on (`RATE_LIMIT_ENABLED`, default `true`) and a client IP sent more than `RATE_LIMIT_PER_MINUTE` (default `60`) requests in a minute; `/health` and `/ready` are exempt. The counter is per uvicorn worker, not shared |

## Outlook Autodiscover Example

Request:

```bash
curl -i -X POST https://autodiscover.example.com/autodiscover/autodiscover.xml \
  -H "Content-Type: text/xml" \
  --data '<Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/requestschema/2006">
  <Request>
    <EMailAddress>user@example.com</EMailAddress>
    <AcceptableResponseSchema>http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a</AcceptableResponseSchema>
  </Request>
</Autodiscover>'
```

Only the `EMailAddress` element is read (its XML namespace is ignored); everything else in the body is ignored. Response for `IMAP_HOST=mail.example.com`, `IMAP_PORT=993`, `IMAP_SOCKET_TYPE=SSL`, `SMTP_PORT=587`, `SMTP_SOCKET_TYPE=STARTTLS`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/responseschema/2006">
  <Response xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a">
    <Account>
      <AccountType>email</AccountType>
      <Action>settings</Action>

      <Protocol>
        <Type>IMAP</Type>
        <Server>mail.example.com</Server>
        <Port>993</Port>
        <DomainRequired>off</DomainRequired>
        <LoginName>user@example.com</LoginName>
        <SPA>off</SPA>
        <SSL>on</SSL>
        <AuthRequired>on</AuthRequired>
      </Protocol>

      <Protocol>
        <Type>SMTP</Type>
        <Server>mail.example.com</Server>
        <Port>587</Port>
        <DomainRequired>off</DomainRequired>
        <LoginName>user@example.com</LoginName>
        <SPA>off</SPA>
        <SSL>on</SSL>
        <AuthRequired>on</AuthRequired>
        <UsePOPAuth>off</UsePOPAuth>
        <SMTPLast>off</SMTPLast>
      </Protocol>
    </Account>
  </Response>
</Autodiscover>
```

`LoginName` follows `USERNAME_FORMAT` (the full address by default). The `SSL` element is `on` for both `SSL` and `STARTTLS` socket types and `off` otherwise. Outlook's response has no POP3 block; POP3 is offered to Thunderbird only.

## Thunderbird And Apple Mail Examples

```bash
curl -i "https://autoconfig.example.com/mail/config-v1.1.xml?emailaddress=user@example.com"
curl -i "https://autodiscover.example.com/mail/ios.mobileconfig?emailaddress=user@example.com"
```

The Thunderbird response is a `<clientConfig version="1.1">` document with one `incomingServer type="imap"`, an optional `incomingServer type="pop3"` when POP3 is enabled, and one `outgoingServer type="smtp"`. The Apple Mail response is an unsigned configuration profile that never contains a password.

For where these hostnames point and how the reverse proxy should forward them, see [dns.md](dns.md) and [reverse-proxy/](reverse-proxy/).
