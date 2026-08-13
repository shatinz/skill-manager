---
id: security-sast-hardening.secrets-management.secret-leak-precommit-guard
name: secret-leak-precommit-guard
title: Secret Leak Prevention, Gitleaks & Pre-Commit Git Guards
category: security-sast-hardening
subcategory: secrets-management
version: 1.2.0
tags:
- secrets
- gitleaks
- pre-commit
- security
- git-hooks
- environment-variables
trust_rating: 0.99
estimated_tokens: 1450
description: Prevent accidental commits of API keys, private tokens, and passwords
  using Gitleaks, automated pre-commit git hooks, and CI repository scanners.
trigger_patterns:
- prevent secret leaks gitleaks
- pre-commit hook gitleaks setup
- scan repo for exposed api keys
- git filter repo remove committed secrets
---

# Secret Leak Prevention, Gitleaks & Pre-Commit Git Guards

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
