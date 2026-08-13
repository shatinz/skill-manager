"""
Category 3: Databases & Storage (6 Skills)
"""

DATABASES_STORAGE_SKILLS = [
    {
        "id": "databases-storage.relational-sql.postgres-query-tuning",
        "name": "postgres-query-tuning",
        "title": "PostgreSQL Query Tuning, Indexing & EXPLAIN BUFFERS",
        "category": "databases-storage",
        "subcategory": "relational-sql",
        "version": "1.5.0",
        "tags": ["postgres", "sql", "explain-analyze", "indexes", "gin", "brin", "performance"],
        "trust_rating": 0.99,
        "estimated_tokens": 1650,
        "description": "Diagnose query bottlenecks, inspect EXPLAIN (ANALYZE, BUFFERS) execution trees, design composite, partial, and GIN indexes, eliminate sequential scans, and optimize PostgreSQL connection parameters.",
        "trigger_patterns": [
            "optimize slow postgres query",
            "postgres explain analyze buffers",
            "postgres composite partial gin index",
            "fix sequential scan postgres",
            "tune postgresql query plan"
        ],
        "content": """# PostgreSQL Query Tuning, Indexing & EXPLAIN BUFFERS

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
"""
    },

    {
        "id": "databases-storage.backend-as-a-service.supabase-realtime-auth-rls",
        "name": "supabase-realtime-auth-rls",
        "title": "Supabase Postgres Row-Level Security (RLS) & Realtime Channels",
        "category": "databases-storage",
        "subcategory": "backend-as-a-service",
        "version": "1.3.0",
        "tags": ["supabase", "rls", "postgres", "realtime", "auth", "row-level-security"],
        "trust_rating": 0.98,
        "estimated_tokens": 1600,
        "description": "Architect impenetrable PostgreSQL Row-Level Security (RLS) policies, manage JWT role claims, and handle multi-client real-time state synchronization using Supabase Realtime channels.",
        "trigger_patterns": [
            "supabase rls policy setup",
            "postgres row level security auth.uid",
            "supabase realtime broadcast presence",
            "supabase multi tenant rls"
        ],
        "content": """# Supabase Postgres Row-Level Security (RLS) & Realtime Channels

## Objective
Enforce database-level multi-tenant security using PostgreSQL RLS policies with `auth.uid()`, coupled with real-time broadcast and presence subscriptions via the Supabase client.

## Bulletproof Multi-Tenant RLS Blueprint
```sql
-- Enable RLS on core tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE org_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 1. Helper function to check organization membership without recursive policy queries
CREATE OR REPLACE FUNCTION is_org_member(_org_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1 FROM org_memberships
    WHERE org_id = _org_id
      AND user_id = auth.uid()
  );
$$;

-- 2. Documents Policy: Read access for organization members
CREATE POLICY "Users can read documents belonging to their organizations"
ON documents
FOR SELECT
TO authenticated
USING (
  is_org_member(org_id)
);

-- 3. Documents Policy: Insert access with ownership assignment
CREATE POLICY "Users can create documents in their organizations"
ON documents
FOR INSERT
TO authenticated
WITH CHECK (
  is_org_member(org_id) AND
  created_by = auth.uid()
);
```

## TypeScript Realtime Channel Integration
```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_ANON_KEY!);

export function subscribeToDocumentChanges(orgId: string, onUpdate: (payload: any) => void) {
  const channel = supabase
    .channel(`org-docs:${orgId}`)
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'documents',
        filter: `org_id=eq.${orgId}`,
      },
      (payload) => {
        onUpdate(payload);
      }
    )
    .subscribe((status) => {
      if (status === 'SUBSCRIBED') {
        console.log('Realtime document channel active');
      }
    });

  return () => {
    supabase.removeChannel(channel);
  };
}
```

## Anti-Patterns
- ❌ Relying on client-side WHERE clauses for security instead of declarative RLS policies.
- ❌ Calling un-indexed subqueries inside RLS `USING` expressions (kills query throughput at scale).
"""
    },

    {
        "id": "databases-storage.orm-data-access.prisma-orm-mastery",
        "name": "prisma-orm-mastery",
        "title": "Prisma ORM Type-Safe Modeling, Relations & Accelerate",
        "category": "databases-storage",
        "subcategory": "orm-data-access",
        "version": "1.3.0",
        "tags": ["prisma", "typescript", "orm", "migrations", "relations", "connection-pooling"],
        "trust_rating": 0.96,
        "estimated_tokens": 1500,
        "description": "Design relational database schemas, manage zero-downtime Prisma migrations, optimize complex queries with nested includes, and configure connection pooling.",
        "trigger_patterns": [
            "prisma schema relations",
            "prisma migrate deploy production",
            "prisma $transaction batch queries",
            "prisma connection pooling accelerate"
        ],
        "content": """# Prisma ORM Type-Safe Modeling & Migrations

## Objective
Model relational structures in Prisma Schema language, execute safe ACID transactions, eliminate N+1 queries using targeted includes/selects, and streamline CI migration pipelines.

## Schema Modeling (`prisma/schema.prisma`)
```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id        String    @id @default(uuid())
  email     String    @unique
  name      String?
  posts     Post[]
  profile   Profile?
  createdAt DateTime  @default(now())

  @@index([createdAt])
  @@map("users")
}

model Post {
  id        String   @id @default(uuid())
  title     String   @db.VarChar(255)
  published Boolean  @default(false)
  authorId  String
  author    User     @relation(fields: [authorId], references: [id], onDelete: Cascade)

  @@index([authorId, published])
  @@map("posts")
}
```

## Transactional Query Pattern (`lib/posts.ts`)
```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function publishPostWithAudit(authorId: string, title: string) {
  return await prisma.$transaction(async (tx) => {
    const post = await tx.post.create({
      data: {
        title,
        published: true,
        authorId,
      },
      include: {
        author: {
          select: { id: true, email: true },
        },
      },
    });

    return post;
  });
}
```

## Anti-Patterns
- ❌ Running `prisma db push` in production; always use `prisma migrate deploy`.
- ❌ Over-fetching data by returning unbounded nested relations without `select` or `take` limits.
"""
    },

    {
        "id": "databases-storage.orm-data-access.drizzle-orm-type-safe",
        "name": "drizzle-orm-type-safe",
        "title": "Drizzle ORM Zero-Overhead SQL-First Schema & Queries",
        "category": "databases-storage",
        "subcategory": "orm-data-access",
        "version": "1.3.0",
        "tags": ["drizzle-orm", "typescript", "postgres", "sqlite", "type-safety", "sql"],
        "trust_rating": 0.98,
        "estimated_tokens": 1550,
        "description": "Construct ultra-fast, zero-runtime-overhead database layers with Drizzle ORM, schema-as-code definitions, relational queries, prepared statements, and drizzle-kit migrations.",
        "trigger_patterns": [
            "drizzle orm schema typescript",
            "drizzle kit migrate push",
            "drizzle relational queries db.query",
            "drizzle prepared statement sql"
        ],
        "content": """# Drizzle ORM Zero-Overhead SQL-First Schema & Queries

## Objective
Build lightweight, SQL-transparent, end-to-end type-safe database layers with Drizzle ORM and Drizzle Kit migrations, achieving maximum query execution speed and zero bundle bloat.

## Schema Definition (`db/schema.ts`)
```typescript
import { pgTable, uuid, varchar, text, timestamp, boolean, index } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  fullName: varchar('full_name', { length: 120 }),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const teams = pgTable('teams', {
  id: uuid('id').primaryKey().defaultRandom(),
  name: varchar('name', { length: 100 }).notNull(),
  ownerId: uuid('owner_id').references(() => users.id, { onDelete: 'cascade' }).notNull(),
}, (table) => ({
  ownerIdx: index('team_owner_idx').on(table.ownerId),
}));

export const usersRelations = relations(users, ({ many }) => ({
  teams: many(teams),
}));

export const teamsRelations = relations(teams, ({ one }) => ({
  owner: one(users, {
    fields: [teams.ownerId],
    references: [users.id],
  }),
}));
```

## Relational Querying & Prepared Statements (`db/queries.ts`)
```typescript
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import { eq, sql } from 'drizzle-orm';
import * as schema from './schema';

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
export const db = drizzle(pool, { schema });

// Prepared statement for high-throughput execution
export const getUserByIdPrepared = db.query.users
  .findFirst({
    where: eq(schema.users.id, sql.placeholder('userId')),
    with: {
      teams: true,
    },
  })
  .prepare('get_user_by_id');

export async function fetchUserWithTeams(userId: string) {
  return await getUserByIdPrepared.execute({ userId });
}
```

## Anti-Patterns
- ❌ Creating multiple unmanaged `Pool` instances across serverless edge functions.
- ❌ Skipping indexes on foreign key columns defined in schema files.
"""
    },

    {
        "id": "databases-storage.olap-embedded.duckdb-polars-analytics",
        "name": "duckdb-polars-analytics",
        "title": "DuckDB & Polars High-Speed Embedded OLAP Analytics",
        "category": "databases-storage",
        "subcategory": "olap-embedded",
        "version": "1.3.0",
        "tags": ["duckdb", "polars", "python", "arrow", "parquet", "olap", "analytics"],
        "trust_rating": 0.97,
        "estimated_tokens": 1550,
        "description": "Perform high-speed in-process analytical SQL queries, zero-copy Arrow data transfers, and lazy DataFrame aggregations over gigabytes of Parquet files using DuckDB and Polars.",
        "trigger_patterns": [
            "duckdb polars fast analytics",
            "duckdb scan parquet files sql",
            "polars lazy dataframe query",
            "duckdb arrow zero copy python"
        ],
        "content": """# DuckDB & Polars High-Speed Embedded OLAP Analytics

## Objective
Process multi-gigabyte datasets directly in-process with sub-second response times using DuckDB columnar SQL execution, Polars lazy evaluation, and zero-copy Apache Arrow buffers.

## Production Python Analytics Pipeline
```python
import duckdb
import polars as pl

def analyze_telemetry_dataset(parquet_glob: str) -> pl.DataFrame:
    # 1. Initialize DuckDB in-memory engine with multithreading
    con = duckdb.connect(database=":memory:")
    con.execute("PRAGMA threads=8;")
    con.execute("PRAGMA memory_limit='8GB';")

    # 2. Query Parquet files directly without loading raw data into memory
    query = (
        "SELECT "
        "  service_name, "
        "  date_trunc('hour', timestamp) AS hour_bucket, "
        "  count(*) AS total_requests, "
        "  avg(duration_ms) AS avg_duration, "
        "  quantile_cont(duration_ms, 0.99) AS p99_duration, "
        "  sum(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END) AS error_count "
        f"FROM read_parquet('{parquet_glob}') "
        "WHERE timestamp >= now() - INTERVAL '7 days' "
        "GROUP BY service_name, hour_bucket "
        "HAVING count(*) > 100 "
        "ORDER BY hour_bucket DESC, p99_duration DESC;"
    )
    
    # 3. Export to Apache Arrow and convert to Polars LazyFrame with zero-copy
    arrow_table = con.execute(query).arrow()
    df = pl.from_arrow(arrow_table)

    # 4. Perform further transformations in Polars
    result = (
        df.lazy()
        .with_columns(
            (pl.col("error_count") / pl.col("total_requests") * 100).alias("error_rate_pct")
        )
        .filter(pl.col("error_rate_pct") > 1.0)
        .collect()
    )

    return result
```

## Anti-Patterns
- ❌ Loading massive CSV/Parquet files entirely into memory with Pandas before filtering.
- ❌ Running OLTP transaction workloads on columnar OLAP engines like DuckDB.
"""
    },

    {
        "id": "databases-storage.key-value-cache.redis-caching-rate-limiting",
        "name": "redis-caching-rate-limiting",
        "title": "Redis High-Performance Caching, Sliding Window Rate Limiting & Pub/Sub",
        "category": "databases-storage",
        "subcategory": "key-value-cache",
        "version": "1.4.0",
        "tags": ["redis", "caching", "rate-limiting", "lua", "sliding-window", "ioredis"],
        "trust_rating": 0.98,
        "estimated_tokens": 1600,
        "description": "Implement robust Redis cache-aside patterns with jittered TTLs, atomic Lua sliding window rate limiters, distributed locks with Redlock, and Pub/Sub event streams.",
        "trigger_patterns": [
            "redis sliding window rate limit lua",
            "redis cache aside ttl jitter",
            "redis distributed lock redlock",
            "ioredis connection pool rate limiting"
        ],
        "content": """# Redis High-Performance Caching & Sliding Window Rate Limiting

## Objective
Deliver low-latency caching strategies that eliminate cache stampedes, implement atomic sliding window rate limiters via Redis Lua scripts, and manage cluster failover safely.

## Atomic Sliding Window Rate Limiter (Lua Script)
```typescript
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

const SLIDING_WINDOW_LUA = `
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

local clearBefore = now - window
redis.call('ZREMRANGEBYSCORE', key, 0, clearBefore)
local currentRequests = redis.call('ZCARD', key)

if currentRequests < limit then
    redis.call('ZADD', key, now, now)
    redis.call('EXPIRE', key, math.ceil(window / 1000))
    return {1, limit - currentRequests - 1}
else
    return {0, 0}
end
`;

export async function checkRateLimit(
  identifier: string,
  limit: number = 60,
  windowMs: number = 60000
): Promise<{ allowed: boolean; remaining: number }> {
  const key = `ratelimit:${identifier}`;
  const now = Date.now();

  const [allowed, remaining] = (await redis.eval(
    SLIDING_WINDOW_LUA,
    1,
    key,
    now,
    windowMs,
    limit
  )) as [number, number];

  return {
    allowed: allowed === 1,
    remaining,
  };
}
```

## Cache-Aside with Jitter (Preventing Thundering Herd)
```typescript
export async function getCachedWithJitter<T>(
  key: string,
  baseTtlSeconds: number,
  fetchFn: () => Promise<T>
): Promise<T> {
  const cached = await redis.get(key);
  if (cached) {
    return JSON.parse(cached) as T;
  }

  const freshData = await fetchFn();
  // Apply +/- 15% TTL jitter
  const jitter = Math.floor(baseTtlSeconds * (0.85 + Math.random() * 0.3));
  await redis.set(key, JSON.stringify(freshData), 'EX', jitter);

  return freshData;
}
```

## Anti-Patterns
- ❌ Running `KEYS *` in production Redis (blocks the single-threaded engine). Use `SCAN` instead.
- ❌ Omitting TTLs on cache entries, leading to silent memory exhaustion (OOM).
"""
    }
]
