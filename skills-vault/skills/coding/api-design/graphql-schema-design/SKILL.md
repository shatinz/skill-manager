---
id: coding.api-design.graphql-schema-design
name: graphql-schema-design
title: GraphQL Schema Architecture & Federation
category: coding
subcategory: api-design
version: 1.0.0
tags:
- graphql
- strawberry
- apollo
- schema
- api
- python
- typescript
trust_rating: 0.91
estimated_tokens: 1200
description: Design modular, scalable GraphQL schemas with type safety, DataLoader
  N+1 query batching, relay-style cursor pagination, and schema-first evolution.
trigger_patterns:
- design graphql schema
- fix n+1 graphql dataloader
- strawberry graphql python
- graphql cursor pagination
- apollo federation schema
---

# GraphQL Schema Architecture & Federation

## Objective
Design robust GraphQL APIs that prevent N+1 query cascades, support Relay cursor pagination, and enforce strict type definitions.

## Key Principles
1. **DataLoader Optimization**: Every relational field resolver MUST use a batch DataLoader to collapse $N$ queries into a single batch query.
2. **Relay Cursor Connections**: Use `edges`, `node`, `pageInfo`, and opaque cursors for all collection fields.
3. **Mutation Responses**: Always return an object with a payload and user-facing error list, not bare booleans or raw entity types.

## Verification Checklist
- Run DataLoader benchmarks to confirm batching collapses queries.
- Verify introspection query performance and enforce query depth limiting.
