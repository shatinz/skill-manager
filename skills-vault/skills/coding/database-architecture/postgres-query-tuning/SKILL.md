---
id: coding.database-architecture.postgres-query-tuning
name: postgres-query-tuning
title: PostgreSQL Performance Optimization & Query Tuning
category: coding
subcategory: database-architecture
version: 1.3.0
tags:
- postgres
- sql
- performance
- indexing
- explain-analyze
- database
trust_rating: 0.98
estimated_tokens: 1600
description: Diagnose slow SQL queries, analyze EXPLAIN (ANALYZE, BUFFERS) plans,
  design composite/partial/BRIN indexes, and tune PostgreSQL memory parameters.
trigger_patterns:
- optimize slow sql query
- postgres explain analyze
- design postgres indexes
- tune postgres database performance
- resolve sequential scan postgres
---

# PostgreSQL Performance Optimization & Query Tuning

## Objective
Transform high-latency SQL queries into microsecond execution plans using advanced indexing strategies, query rewriting, and buffer inspection.

## Execution Analysis Workflow
1. Run `EXPLAIN (ANALYZE, BUFFERS, SETTINGS) <query>;`
2. Check `Buffers: shared hit=... read=...`. High `read` indicates disk I/O bottlenecks.
3. Identify `Seq Scan` on large tables, `Hash Join` with excessive batch spillage, and expensive `Sort` operations.

## Indexing Decision Matrix
- **B-Tree**: Default equality, range (`<`, `<=`, `>=`, `>`), and `ORDER BY`.
- **Composite Index**: Put high-cardinality equality columns first, followed by range column: `CREATE INDEX ON orders (user_id, status, created_at DESC);`.
- **Partial Index**: For filtered hot sets: `CREATE INDEX ON tasks (priority) WHERE status = 'pending';`.
- **GIN**: For JSONB containment (`@>`), full-text search (`tsvector`), and array overlap (`&&`).
