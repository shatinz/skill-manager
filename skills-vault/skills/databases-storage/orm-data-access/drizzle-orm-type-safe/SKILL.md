---
id: databases-storage.orm-data-access.drizzle-orm-type-safe
name: drizzle-orm-type-safe
title: Drizzle ORM Zero-Overhead SQL-First Schema & Queries
category: databases-storage
subcategory: orm-data-access
version: 1.3.0
tags:
- drizzle-orm
- typescript
- postgres
- sqlite
- type-safety
- sql
trust_rating: 0.98
estimated_tokens: 1550
description: Construct ultra-fast, zero-runtime-overhead database layers with Drizzle
  ORM, schema-as-code definitions, relational queries, prepared statements, and drizzle-kit
  migrations.
trigger_patterns:
- drizzle orm schema typescript
- drizzle kit migrate push
- drizzle relational queries db.query
- drizzle prepared statement sql
---

# Drizzle ORM Zero-Overhead SQL-First Schema & Queries

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
