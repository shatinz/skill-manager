---
id: testing-quality.security-sast.secret-leak-detector
name: secret-leak-detector
title: Automated Secret Leak Detection & Git Pre-Commit Guard
category: testing-quality
subcategory: security-sast
version: 1.0.0
tags:
- secrets
- gitleaks
- git-guard
- security
- api-keys
trust_rating: 0.95
estimated_tokens: 1100
description: Prevent accidental commits of API keys, private certificates, JWT secrets,
  and database credentials using regex entropy patterns and pre-commit hooks.
trigger_patterns:
- detect leaked secrets
- scan for api keys in code
- gitleaks pre-commit setup
- prevent credential leak
---

# Automated Secret Leak Detection & Git Pre-Commit Guard

## Rules
- Match high-entropy strings and vendor prefix tokens (`sk_live_`, `ghp_`, `AKIA...`, `BEGIN RSA PRIVATE KEY`).
- Block commits with `pre-commit` and run Gitleaks in CI before merges.
