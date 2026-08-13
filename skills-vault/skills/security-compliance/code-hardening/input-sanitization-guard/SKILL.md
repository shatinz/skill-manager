---
id: security-compliance.code-hardening.input-sanitization-guard
name: input-sanitization-guard
title: Input Sanitization, Schema Validation & XSS Defense
category: security-compliance
subcategory: code-hardening
version: 1.0.0
tags:
- sanitization
- xss
- security
- validation
- pydantic
- zod
trust_rating: 0.93
estimated_tokens: 1200
description: Defend against DOM XSS, prototype pollution, HTML injection, and untrusted
  payload deserialization using strict schema boundaries (Zod/Pydantic) and DOMPurify.
trigger_patterns:
- input sanitization security
- prevent xss attacks
- validate untrusted input
- dompurify sanitize html
---

# Input Sanitization, Schema Validation & XSS Defense

## Validation Directives
- Parse and strip all untrusted HTML through DOMPurify with strict allowed tags.
- Reject unknown object keys in API payloads (`extra='forbid'`).
