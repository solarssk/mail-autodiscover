# Home

Welcome to the `mail-autodiscover` wiki.

This documentation is written for admins who run a self-hosted mail server and want Outlook, Thunderbird, or Apple Mail to discover the correct IMAP and SMTP settings automatically.

## Start here

- [What This Project Does](What-This-Project-Does)
- [Quick Start](Quick-Start)
- [Deployment with Docker or Portainer](Deployment-with-Docker-or-Portainer)
- [Reverse Proxy and DNS](Reverse-Proxy-and-DNS)
- [Client Setup: Outlook, Thunderbird, Apple Mail](Client-Setup-Outlook-Thunderbird-Apple-Mail)
- [Configuration Reference](Configuration-Reference)
- [Upgrade Guide](Upgrade-Guide)
- [Security Model](Security-Model)
- [Troubleshooting](Troubleshooting)

## What you should know first

- This project is not a mail server.
- It returns client settings based on your environment variables.
- It does not verify whether a mailbox exists.
- It is designed for simple, predictable deployments with shared IMAP/SMTP settings per domain.

## Recommended reading path

1. Read [What This Project Does](What-This-Project-Does).
2. Follow [Quick Start](Quick-Start).
3. Before production, review [Reverse Proxy and DNS](Reverse-Proxy-and-DNS) and [Security Model](Security-Model).
4. When upgrading, use [Upgrade Guide](Upgrade-Guide).
