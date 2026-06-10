# mail-autodiscover

Lekki serwis HTTP do automatycznej konfiguracji klientów pocztowych (Outlook Autodiscover i Thunderbird Autoconfig) dla self-hosted serwerów poczty, w szczególności **Synology MailPlus Server**.

## Czego to nie robi

- Nie jest serwerem poczty
- Nie zastępuje Synology MailPlus Server
- Nie implementuje Exchange, EWS ani ActiveSync
- Nie obsługuje kalendarzy ani kontaktów
- Nie sprawdza, czy skrzynka pocztowa istnieje

## Jak działa

Klient pocztowy (Outlook, Thunderbird) wysyła zapytanie na endpoint autodiscover/autoconfig. Serwis zwraca XML z ustawieniami IMAP/SMTP na podstawie konfiguracji z zmiennych środowiskowych.

Dla każdego poprawnego adresu `@dozwolona-domena` zwracana jest **ta sama konfiguracja** — bez weryfikacji istnienia konta.

## Security model

- **Brak enumeracji skrzynek** — serwis nie łączy się z Synology API, LDAP ani IMAP
- **Brak logowania adresów e-mail** — logi zawierają tylko `request_id`, endpoint, status i `domain_allowed=true/false`
- **Rate limiting** — in-memory, per IP (`RATE_LIMIT_PER_MINUTE`)
- **Bezpieczne parsowanie XML** — `defusedxml`, limit rozmiaru body
- **Security headers** — `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`, `Cache-Control: no-store`
- **Brak panelu admina w MVP** — konfiguracja wyłącznie przez ENV
- **Brak publicznej listy domen** — endpoint `/` nie ujawnia hostów ani domen

## Szybki start

### Przykładowy `.env`

```env
APP_NAME=mail-autodiscover
APP_ENV=production
PUBLIC_BASE_URL=https://autodiscover.example.com
ALLOWED_DOMAINS=example.com
MAIL_DISPLAY_NAME=Example Mail
MAIL_DISPLAY_SHORT_NAME=Example
IMAP_HOST=mail.example.com
IMAP_PORT=993
IMAP_SOCKET_TYPE=SSL
SMTP_HOST=mail.example.com
SMTP_PORT=587
SMTP_SOCKET_TYPE=STARTTLS
USERNAME_FORMAT=email
```

Pełna lista zmiennych: [.env.example](.env.example)

### Docker Compose

```bash
cp .env.example .env
# edytuj .env według potrzeb
docker compose up -d --build
```

### Lokalnie (bez Dockera)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install ".[dev]"
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpointy

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| `GET` | `/health` | Healthcheck |
| `GET` | `/` | Nazwa aplikacji i status |
| `GET` | `/mail/config-v1.1.xml?emailaddress=...` | Thunderbird Autoconfig |
| `GET` | `/.well-known/autoconfig/mail/config-v1.1.xml?emailaddress=...` | Thunderbird (well-known) |
| `POST` | `/autodiscover/autodiscover.xml` | Outlook Autodiscover |
| `GET` | `/autodiscover/autodiscover.xml` | Neutralna odpowiedź Outlook |

## Reverse proxy

Skieruj ruch na kontener:

```text
https://autodiscover.example.com/autodiscover/autodiscover.xml
https://autoconfig.example.com/mail/config-v1.1.xml
https://autoconfig.example.com/.well-known/autoconfig/mail/config-v1.1.xml
```

Ustaw `TRUST_PROXY_HEADERS=true` tylko gdy aplikacja stoi za zaufanym reverse proxy (nginx, Caddy, Traefik). W przeciwnym razie nagłówek `X-Forwarded-For` może być fałszowany.

## DNS

Przykładowe rekordy:

```text
autodiscover.example.com  CNAME  proxy.example.com
autoconfig.example.com    CNAME  proxy.example.com
mail.example.com          A/CNAME  <serwer poczty>
```

Opcjonalnie rekordy SRV:

```text
_imaps._tcp.example.com.       SRV 0 1 993 mail.example.com.
_submission._tcp.example.com.  SRV 0 1 587 mail.example.com.
```

## Testowanie (curl)

### Thunderbird

```bash
curl "http://localhost:8088/mail/config-v1.1.xml?emailaddress=user@example.com"
```

### Outlook

```bash
curl -X POST "http://localhost:8088/autodiscover/autodiscover.xml" \
  -H "Content-Type: text/xml" \
  --data '<?xml version="1.0" encoding="utf-8"?><Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/requestschema/2006"><Request><EMailAddress>user@example.com</EMailAddress><AcceptableResponseSchema>http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a</AcceptableResponseSchema></Request></Autodiscover>'
```

## Testy

```bash
pip install ".[dev]"
pytest -v
ruff check .
```

## Roadmap

### v0.1 (MVP)

- Konfiguracja przez ENV
- Outlook Autodiscover
- Thunderbird Autoconfig
- Docker + Docker Compose
- Testy + GitHub Actions CI

### v0.2

- Multi-domain config per domena
- Różne hosty IMAP/SMTP per domena
- Lepszy rate limiting
- Opcjonalny POP3

### v0.3

- Panel administracyjny
- Baza danych
- Logowanie OIDC przez Authentik
- Role admin/viewer
- Audyt zmian konfiguracji

### v0.4

- SAML/OIDC hardening
- Backup/restore config
- Import/export config
- Publikacja obrazu Docker do GHCR

## Licencja

MIT — zobacz [LICENSE](LICENSE).
