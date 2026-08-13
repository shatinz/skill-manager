---
id: security-sast-hardening.auth-security.jwt-oauth2-secureshop
name: jwt-oauth2-secureshop
title: JWT & OAuth2 Secure Authentication & Token Rotation
category: security-sast-hardening
subcategory: auth-security
version: 1.3.0
tags:
- jwt
- oauth2
- authentication
- token-rotation
- refresh-token
- pkce
- security
trust_rating: 0.98
estimated_tokens: 1600
description: Implement cryptographically secure JWT authentication flows with asymmetric
  key signing (RS256), sliding refresh token rotation, HttpOnly SameSite cookies,
  and PKCE.
trigger_patterns:
- jwt refresh token rotation
- oauth2 pkce authorization code
- secure jwt httponly cookie
- jwt rs256 asymmetric signing
---

# JWT & OAuth2 Secure Authentication & Token Rotation

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
