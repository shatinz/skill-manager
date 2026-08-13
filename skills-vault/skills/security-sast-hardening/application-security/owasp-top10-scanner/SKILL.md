---
id: security-sast-hardening.application-security.owasp-top10-scanner
name: owasp-top10-scanner
title: OWASP Top 10 Vulnerability Audit & Defense Craft
category: security-sast-hardening
subcategory: application-security
version: 1.4.0
tags:
- owasp
- security
- sast
- injection
- broken-auth
- csrf
- ssrf
- defense
trust_rating: 0.99
estimated_tokens: 1650
description: Perform comprehensive code audits against the OWASP Top 10 vulnerabilities
  (SQL/Command Injection, Broken Auth, SSRF, IDOR, Security Misconfigurations) with
  concrete automated remediation.
trigger_patterns:
- owasp top 10 vulnerability scan
- prevent ssrf injection vulnerability
- idor broken access control fix
- sast security audit checklist
---

# OWASP Top 10 Vulnerability Audit & Defense Craft

## Objective
Audit and harden web applications against the OWASP Top 10 critical security risks, implementing defense-in-depth sanitization, SSRF filters, and parameterized queries.

## Critical Defense Matrix
1. **Injection (A03)**: Always use parameterized queries / ORMs. Never concatenate user strings into SQL or OS commands.
2. **Server-Side Request Forgery - SSRF (A10)**: Validate and resolve hostnames, blocking requests to internal metadata IP ranges (`169.254.169.254`, `127.0.0.1`, `10.0.0.0/8`).
3. **Broken Access Control / IDOR (A01)**: Verify tenant ownership of requested resources (`WHERE id = :id AND org_id = :org_id`).

## SSRF Defense Filter Blueprint (`security/ssrf.py`)
```python
import socket
import ipaddress
import urllib.parse

BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.169.254/32"), # AWS/GCP Metadata
]

def validate_safe_outgoing_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False

    hostname = parsed.hostname
    if not hostname:
        return False

    # Resolve all IPs for hostname
    try:
        ip_addresses = socket.getaddrinfo(hostname, None)
        for addr in ip_addresses:
            ip_obj = ipaddress.ip_address(addr[4][0])
            for blocked in BLOCKED_NETWORKS:
                if ip_obj in blocked:
                    return False
    except Exception:
        return False

    return True
```

## Anti-Patterns
- ❌ Disabling SSL certificate verification (`verify=False`).
- ❌ Relying solely on client-side validation to block malicious payloads.
