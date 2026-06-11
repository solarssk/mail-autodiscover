# Outlook

## What Users Do

1. Add the mailbox address in Outlook.
2. Enter the mailbox password when prompted.
3. Outlook should discover IMAP/SMTP settings through `POST /autodiscover/autodiscover.xml`.

## Admin Validation

- verify `autodiscover.<domain>` resolves publicly
- verify HTTPS certificate is valid
- verify the mailbox domain is allowed in ENV mode or present in YAML mode

## Notes

The application returns a neutral response on `GET /autodiscover/autodiscover.xml` to handle generic probes safely.
