---
id: security-compliance.code-hardening.jwt-oauth2-secureshop
name: jwt-oauth2-secureshop
title: OAuth2 & JWT Token Security Architecture
category: security-compliance
subcategory: code-hardening
version: 1.2.0
tags:
- oauth2
- jwt
- auth
- security
- tokens
- fastapi
- nodejs
trust_rating: 0.97
estimated_tokens: 1450
description: Implement bulletproof JWT authentication and OAuth2 token lifecycles
  with asymmetric RS256/EdDSA signing, token revocation blacklists, and rotation.
trigger_patterns:
- implement secure jwt auth
- oauth2 token rotation
- jwt rs256 asymmetric signing
- refresh token revocation
---

# OAuth2 & JWT Token Security Architecture

## Security Invariants
1. **Algorithm Whitelist**: Strictly enforce `algorithm="RS256"` or `"EdDSA"`. Never trust header `alg: none`.
2. **Short-Lived Access Tokens**: 5 to 15 minutes validity max.
3. **Opaque Refresh Tokens**: Store hashed in Redis with single-use rotation detection.
