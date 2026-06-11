# What This Project Does

`mail-autodiscover` helps mail clients configure themselves for your self-hosted mail server.

Instead of asking users to type in IMAP and SMTP hostnames, ports, and encryption settings by hand, the service answers standard client requests with the settings you define in environment variables.

## Supported clients

- Outlook via Autodiscover
- Thunderbird via Autoconfig
- Apple Mail via downloadable `.mobileconfig` profiles

## What the service actually returns

The response contains:

- mail server hostnames,
- ports,
- socket and authentication types,
- display names,
- username format.

All of those values come from your deployment configuration.

## What it does not do

This project does not:

- provide webmail,
- host mailboxes,
- verify whether a mailbox exists,
- manage calendars or contacts,
- expose an admin UI,
- implement Exchange, EWS, or ActiveSync.

## Why the mailbox check is intentionally missing

The service returns the same configuration shape for any syntactically valid address in an allowed domain.

That behavior is intentional. It prevents the service from becoming a mailbox-enumeration endpoint.
