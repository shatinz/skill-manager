---
id: clean-architecture-refactoring.architectural-docs.adr-architecture-decision-records
name: adr-architecture-decision-records
title: Architecture Decision Records (ADR) Craft & Review
category: clean-architecture-refactoring
subcategory: architectural-docs
version: 1.3.0
tags:
- adr
- architecture
- decision-records
- documentation
- rfc
- governance
trust_rating: 0.99
estimated_tokens: 1400
description: Document, evaluate, and track critical architectural trade-offs using
  structured Michael Nygard Architecture Decision Record (ADR) templates and decision
  matrices.
trigger_patterns:
- write architecture decision record adr
- adr template michael nygard
- document technical trade offs adr
- architecture decision log governance
---

# Architecture Decision Records (ADR) Craft & Review

## Objective
Preserve long-term institutional knowledge and clarify architectural trade-offs by authoring structured, versioned Architecture Decision Records (ADRs).

## Standard Michael Nygard ADR Template (`docs/adr/0001-adopt-fastapi-and-postgres.md`)
```markdown
# 1. Adopt FastAPI & PostgreSQL for Core Microservice

Date: 2025-02-15
Status: Accepted

## Context
The legacy service struggles with synchronous blocking I/O and lacks type safety, leading to runtime data validation bugs under high concurrency.

## Decision
We will rewrite the core ingestion service in Python 3.12 using FastAPI, Pydantic v2, and SQLAlchemy 2.0 with PostgreSQL.

## Consequences
### Positive
- Native async I/O handles 5,000+ concurrent requests per second.
- Automatic OpenAPI documentation and strict Pydantic runtime schema validation.

### Negative / Trade-offs
- Engineers must adhere strictly to async database sessions and avoid blocking libraries.
```

## Anti-Patterns
- ❌ Authoring ADRs post-hoc without documenting rejected alternatives and negative consequences.
- ❌ Treating ADRs as immutable dogma rather than superseding them with new ADRs when requirements evolve.

## Quality & Verification Checklist
- [ ] Every ADR file follows numbered naming: `docs/adr/NNNN-title.md`.
- [ ] Status is clearly labeled: Proposed, Accepted, Deprecated, or Superseded by NNNN.
