---
id: testing-quality.security-sast.owasp-top10-scanner
name: owasp-top10-scanner
title: OWASP Top 10 SAST Security Auditing & Remediation
category: testing-quality
subcategory: security-sast
version: 1.3.0
tags:
- security
- owasp
- sast
- vulnerability
- audit
- injection
trust_rating: 0.98
estimated_tokens: 1600
description: Scan codebases for OWASP Top 10 vulnerabilities (SQLi, XSS, SSRF, IDOR,
  Broken Auth, Command Injection) and implement robust automated security controls.
trigger_patterns:
- audit owasp vulnerabilities
- security audit code
- fix sql injection xss
- sast security scanning
- check for idor ssrf
---

# OWASP Top 10 SAST Security Auditing & Remediation

## Scan & Audit Rules
1. **Injection (A03)**: Ban string interpolation in SQL/OS queries. Enforce parameterized queries and ORMs.
2. **Broken Access Control (A01)**: Enforce tenant ID verification on every single object lookup (prevent IDOR).
3. **SSRF (A10)**: Validate and whitelist target hosts for server-side outbound webhooks/fetch. Disallow private IP subnets (`127.0.0.1`, `10.0.0.0/8`, `169.254.169.254`).
