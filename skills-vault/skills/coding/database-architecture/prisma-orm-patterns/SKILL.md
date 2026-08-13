---
id: coding.database-architecture.prisma-orm-patterns
name: prisma-orm-patterns
title: Prisma ORM Type-Safe Data Modeling & Migrations
category: coding
subcategory: database-architecture
version: 1.1.0
tags:
- prisma
- typescript
- orm
- database
- migrations
- nodejs
trust_rating: 0.92
estimated_tokens: 1300
description: Master type-safe database access with Prisma ORM in TypeScript, including
  relation queries, interactive transactions, nested writes, and zero-downtime migrations.
trigger_patterns:
- prisma schema design
- prisma interactive transactions
- prisma migrations typescript
- optimize prisma queries
---

# Prisma ORM Type-Safe Data Modeling & Migrations

## Objective
Model complex relational domains in `schema.prisma`, execute atomic interactive transactions, and prevent over-fetching using type-safe select payloads.

## Rules
- Use `$transaction(async (tx) => { ... })` for multi-step mutations.
- Prefer explicit `select` over unbounded `include` to minimize wire payload.
- Always run `prisma migrate dev` during local development and `prisma migrate deploy` in production CI/CD.
