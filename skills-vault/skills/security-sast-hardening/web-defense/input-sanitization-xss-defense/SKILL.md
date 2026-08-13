---
id: security-sast-hardening.web-defense.input-sanitization-xss-defense
name: input-sanitization-xss-defense
title: Input Sanitization, DOMPurify & XSS Defense Craft
category: security-sast-hardening
subcategory: web-defense
version: 1.3.0
tags:
- xss
- sanitization
- dompurify
- csp
- content-security-policy
- security
trust_rating: 0.98
estimated_tokens: 1500
description: Defend modern web applications from Stored, Reflected, and DOM-based
  Cross-Site Scripting (XSS) using DOMPurify sanitization and strict Content Security
  Policies.
trigger_patterns:
- prevent xss dompurify sanitize
- content security policy csp strict
- sanitize user input html xss
- dangerouslySetInnerHTML secure sanitize
---

# Input Sanitization, DOMPurify & XSS Defense Craft

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
