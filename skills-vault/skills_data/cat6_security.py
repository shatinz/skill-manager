"""
Category 6: Security & SAST Hardening (5 Skills)
"""

SECURITY_SAST_SKILLS = [
    {
        "id": "security-sast-hardening.application-security.owasp-top10-scanner",
        "name": "owasp-top10-scanner",
        "title": "OWASP Top 10 Vulnerability Audit & Defense Craft",
        "category": "security-sast-hardening",
        "subcategory": "application-security",
        "version": "1.4.0",
        "tags": ["owasp", "security", "sast", "injection", "broken-auth", "csrf", "ssrf", "defense"],
        "trust_rating": 0.99,
        "estimated_tokens": 1650,
        "description": "Perform comprehensive code audits against the OWASP Top 10 vulnerabilities (SQL/Command Injection, Broken Auth, SSRF, IDOR, Security Misconfigurations) with concrete automated remediation.",
        "trigger_patterns": [
            "owasp top 10 vulnerability scan",
            "prevent ssrf injection vulnerability",
            "idor broken access control fix",
            "sast security audit checklist"
        ],
        "content": """# OWASP Top 10 Vulnerability Audit & Defense Craft

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
"""
    },

    {
        "id": "security-sast-hardening.auth-security.jwt-oauth2-secureshop",
        "name": "jwt-oauth2-secureshop",
        "title": "JWT & OAuth2 Secure Authentication & Token Rotation",
        "category": "security-sast-hardening",
        "subcategory": "auth-security",
        "version": "1.3.0",
        "tags": ["jwt", "oauth2", "authentication", "token-rotation", "refresh-token", "pkce", "security"],
        "trust_rating": 0.98,
        "estimated_tokens": 1600,
        "description": "Implement cryptographically secure JWT authentication flows with asymmetric key signing (RS256), sliding refresh token rotation, HttpOnly SameSite cookies, and PKCE.",
        "trigger_patterns": [
            "jwt refresh token rotation",
            "oauth2 pkce authorization code",
            "secure jwt httponly cookie",
            "jwt rs256 asymmetric signing"
        ],
        "content": """# JWT & OAuth2 Secure Authentication & Token Rotation

## Objective
Construct cryptographically resilient authentication mechanisms using short-lived JWT access tokens, rotating refresh tokens stored in HttpOnly cookies, and PKCE-protected OAuth2 exchanges.

## Refresh Token Rotation Pattern (`auth/tokens.py`)
```python
import jwt
import time
import secrets
import hashlib
from typing import Tuple

SECRET_KEY = "your-private-key-pem"
ALGORITHM = "RS256"

def create_access_token(user_id: str, roles: list) -> str:
    payload = {
        "sub": user_id,
        "roles": roles,
        "iat": int(time.time()),
        "exp": int(time.time()) + 900 # 15 minutes
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def generate_refresh_token() -> Tuple[str, str]:
    # Returns (raw_token_for_cookie, hashed_token_for_db)
    raw_token = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    return raw_token, token_hash
```

## Anti-Patterns
- ❌ Storing access/refresh tokens in browser `localStorage` (accessible via XSS).
- ❌ Accepting unverified `"alg": "none"` in incoming JWT headers.
"""
    },

    {
        "id": "security-sast-hardening.secrets-management.secret-leak-precommit-guard",
        "name": "secret-leak-precommit-guard",
        "title": "Secret Leak Prevention, Gitleaks & Pre-Commit Git Guards",
        "category": "security-sast-hardening",
        "subcategory": "secrets-management",
        "version": "1.2.0",
        "tags": ["secrets", "gitleaks", "pre-commit", "security", "git-hooks", "environment-variables"],
        "trust_rating": 0.99,
        "estimated_tokens": 1450,
        "description": "Prevent accidental commits of API keys, private tokens, and passwords using Gitleaks, automated pre-commit git hooks, and CI repository scanners.",
        "trigger_patterns": [
            "prevent secret leaks gitleaks",
            "pre-commit hook gitleaks setup",
            "scan repo for exposed api keys",
            "git filter repo remove committed secrets"
        ],
        "content": """# Secret Leak Prevention, Gitleaks & Pre-Commit Git Guards

## Objective
Block exposed cloud keys, database passwords, and API tokens from entering git history through automated local pre-commit hooks and CI gate checks.

## Pre-Commit Configuration (`.pre-commit-config.yaml`)
```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.2
    hooks:
      - id: gitleaks

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
      - id: detect-private-key
```

## Anti-Patterns
- ❌ Using `git commit --no-verify` to bypass local pre-commit security hooks.
"""
    },

    {
        "id": "security-sast-hardening.web-defense.input-sanitization-xss-defense",
        "name": "input-sanitization-xss-defense",
        "title": "Input Sanitization, DOMPurify & XSS Defense Craft",
        "category": "security-sast-hardening",
        "subcategory": "web-defense",
        "version": "1.3.0",
        "tags": ["xss", "sanitization", "dompurify", "csp", "content-security-policy", "security"],
        "trust_rating": 0.98,
        "estimated_tokens": 1500,
        "description": "Defend modern web applications from Stored, Reflected, and DOM-based Cross-Site Scripting (XSS) using DOMPurify sanitization and strict Content Security Policies.",
        "trigger_patterns": [
            "prevent xss dompurify sanitize",
            "content security policy csp strict",
            "sanitize user input html xss",
            "dangerouslySetInnerHTML secure sanitize"
        ],
        "content": """# Input Sanitization, DOMPurify & XSS Defense Craft

## Objective
Eliminate XSS injection vulnerabilities by enforcing strict server/client input sanitization and strict Content Security Policy (CSP) headers.

## Secure React HTML Sanitization (`components/SafeHtml.tsx`)
```tsx
import DOMPurify from 'isomorphic-dompurify';

export function SafeHtml({ rawContent }: { rawContent: string }) {
  const sanitized = DOMPurify.sanitize(rawContent, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'ul', 'li', 'code', 'pre'],
    ALLOWED_ATTR: ['href', 'title', 'target'],
    ALLOW_DATA_ATTR: false,
  });

  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
}
```

## Anti-Patterns
- ❌ Rendering unsanitized markdown or user content directly via `dangerouslySetInnerHTML`.
"""
    },

    {
        "id": "security-sast-hardening.supply-chain.dependency-cve-vulnerability-audit",
        "name": "dependency-cve-vulnerability-audit",
        "title": "Software Supply Chain Security, Dependabot & CVE Remediation",
        "category": "security-sast-hardening",
        "subcategory": "supply-chain",
        "version": "1.2.0",
        "tags": ["cve", "supply-chain", "dependabot", "snyk", "npm-audit", "pip-audit", "sbom"],
        "trust_rating": 0.97,
        "estimated_tokens": 1450,
        "description": "Secure the software supply chain through automated SBOM generation, Dependabot configuration, lockfile integrity validation, and CVE vulnerability remediation.",
        "trigger_patterns": [
            "audit cve dependency vulnerabilities",
            "dependabot config setup",
            "generate sbom cyclonedx",
            "pip-audit npm audit supply chain"
        ],
        "content": """# Software Supply Chain Security & CVE Remediation

## Objective
Detect and remediate third-party dependency vulnerabilities before they reach production through automated SBOM generation and lockfile auditing.

## Dependabot Automation (`.github/dependabot.yml`)
```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

## Anti-Patterns
- ❌ Installing packages without deterministic lockfiles (`package-lock.json`, `poetry.lock`).
"""
    }
]
