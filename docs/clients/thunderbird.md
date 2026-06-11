# Thunderbird

## What Users Do

1. Open account setup.
2. Enter name, mailbox address, and password.
3. Thunderbird should fetch config from `/mail/config-v1.1.xml` or the `.well-known` alias.

## Admin Validation

- test with `?emailaddress=user@example.com`
- if POP3 is enabled for a domain, Thunderbird XML should contain a POP3 block
- if POP3 is disabled, only IMAP/SMTP should be returned

## Logging Warning

Thunderbird sends the mailbox address in the query string. Make sure your reverse proxy does not leak that into long-term logs unless you explicitly accept it.
