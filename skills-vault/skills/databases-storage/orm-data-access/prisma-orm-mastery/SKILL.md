---
id: databases-storage.orm-data-access.prisma-orm-mastery
name: prisma-orm-mastery
title: Prisma ORM Type-Safe Modeling, Relations & Accelerate
category: databases-storage
subcategory: orm-data-access
version: 1.3.0
tags:
- prisma
- typescript
- orm
- migrations
- relations
- connection-pooling
trust_rating: 0.96
estimated_tokens: 1500
description: Design relational database schemas, manage zero-downtime Prisma migrations,
  optimize complex queries with nested includes, and configure connection pooling.
trigger_patterns:
- prisma schema relations
- prisma migrate deploy production
- prisma $transaction batch queries
- prisma connection pooling accelerate
---

# Prisma ORM Type-Safe Modeling & Migrations

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
