---
id: databases-storage.relational-sql.postgres-query-tuning
name: postgres-query-tuning
title: PostgreSQL Query Tuning, Indexing & EXPLAIN BUFFERS
category: databases-storage
subcategory: relational-sql
version: 1.5.0
tags:
- postgres
- sql
- explain-analyze
- indexes
- gin
- brin
- performance
trust_rating: 0.99
estimated_tokens: 1650
description: Diagnose query bottlenecks, inspect EXPLAIN (ANALYZE, BUFFERS) execution
  trees, design composite, partial, and GIN indexes, eliminate sequential scans, and
  optimize PostgreSQL connection parameters.
trigger_patterns:
- optimize slow postgres query
- postgres explain analyze buffers
- postgres composite partial gin index
- fix sequential scan postgres
- tune postgresql query plan
---

# PostgreSQL Query Tuning, Indexing & EXPLAIN BUFFERS

## Objective
Transform high-latency SQL queries into microsecond execution plans using buffer analysis, index optimization (B-Tree, Partial, GIN, BRIN), and query restructuring.

## Execution Analysis Methodology
1. **Analyze with Buffers**: Always run `EXPLAIN (ANALYZE, BUFFERS, SETTINGS) <query>;`.
2. **Buffer Hit Ratio**: `Buffers: shared hit=... read=...`. If `read` is high, the query is hitting disk rather than RAM buffer cache (`shared_buffers`).
3. **Plan Inspection Checklist**:
   - Spot `Seq Scan` on tables with > 10,000 rows.
   - Spot `Sort Method: external merge Disk` (indicates `work_mem` is insufficient).
   - Spot large discrepancies between estimated rows and actual rows (run `ANALYZE table_name;`).

## Index Strategy Matrix
- **Composite Index**: For multi-column filters and sorting. Place high-cardinality equality columns first, followed by range/sort columns:
  ```sql
  CREATE INDEX idx_orders_user_status_created ON orders (user_id, status, created_at DESC);
  ```
- **Partial Index**: For filtered hot data sets (drastically reduces index size and write overhead):
  ```sql
  CREATE INDEX idx_active_subscriptions ON subscriptions (user_id) WHERE status = 'ACTIVE';
  ```
- **GIN Index**: For JSONB containment (`@>`) and full-text search (`tsvector`):
  ```sql
  CREATE INDEX idx_events_payload_gin ON events USING gin (payload jsonb_path_ops);
  ```
- **BRIN Index**: For append-only, naturally sorted time-series data on multi-GB tables:
  ```sql
  CREATE INDEX idx_logs_timestamp_brin ON access_logs USING brin (recorded_at);
  ```

## Anti-Patterns
- ❌ Applying functions to indexed columns in WHERE clauses (`WHERE LOWER(email) = '...'`), preventing index usage. Use expression indexes (`CREATE INDEX ON users (LOWER(email));`).
- ❌ Over-indexing write-heavy tables, causing write latency amplification and VACUUM pressure.
