# Thunderbird

The service returns Autoconfig XML 1.1. The laboratory result below covers one specific client build and transport configuration, not every Thunderbird release or operating system. See the [compatibility scope](../../README.md#client-compatibility).

## Recorded validation

On 2026-11-04, a real Thunderbird client completed this isolated end-to-end test against the proposed service version 1.0.0, source commit `936eff5b55ff2592565a72906194ba712f69b11b`:

| Item | Recorded result |
|------|-----------------|
| Client | Mozilla Thunderbird 153.6.0 ESR, Debian package `1:153.6.0esr-1~deb12u2` |
| Client OS | Debian GNU/Linux 12 (bookworm), aarch64 |
| Incoming mail | IMAP, port 993, SSL/TLS, password authentication |
| Outgoing mail | SMTP, port 587, mandatory STARTTLS; server confirmed TLS 1.3 and authenticated submission |
| Discovery | Passed over HTTPS, including `/mail/config-v1.1.xml`; HTTP requests redirected to HTTPS |
| Account setup | Passed in a fresh profile through Account Hub; only name, test email, and test password entered, with no manual host or port edits |
| Sending | Passed using Thunderbird's compose window and Send Now command; Postfix accepted and delivered the message locally |
| Receiving | Passed through Thunderbird's IMAP stack; the test message appeared in Inbox and its full content was read, including the expected body |
| Certificate verification | Enabled; a disposable laboratory CA was trusted only in the test profile, with no certificate exceptions |
| Isolation | Internal Docker network, Internet TCP connectivity blocked, no published host ports, no host profile mounts, and only a fictional `lab.test` mailbox |

The test used Dovecot 2.3.19.1, Postfix 3.7.11, and Nginx 1.22.1. Marionette drove the actual client; it did not substitute a Python SMTP or IMAP client for Thunderbird. The final body read returned success, 937 bytes, and the expected message content.

The full JSON evidence, discovery logs, SMTP/TLS delivery logs, screenshots, and disposable harness were retained as session artifacts. The laboratory is not part of the production service. POP3 was disabled in this scenario and is not certified by this result. This test does not establish Outlook or Apple Mail compatibility.

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
