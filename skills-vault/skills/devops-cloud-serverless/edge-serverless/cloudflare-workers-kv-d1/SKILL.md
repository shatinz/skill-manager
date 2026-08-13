---
id: devops-cloud-serverless.edge-serverless.cloudflare-workers-kv-d1
name: cloudflare-workers-kv-d1
title: Cloudflare Workers, KV, D1 SQL & Durable Objects
category: devops-cloud-serverless
subcategory: edge-serverless
version: 1.3.0
tags:
- cloudflare-workers
- kv
- d1
- durable-objects
- edge
- wrangler
- typescript
trust_rating: 0.98
estimated_tokens: 1600
description: Develop and deploy globally distributed, low-latency edge services using
  Cloudflare Workers, KV caching, D1 relational SQLite storage, and stateful Durable
  Objects.
trigger_patterns:
- cloudflare workers d1 database setup
- cloudflare workers kv binding wrangler
- cloudflare durable objects websocket
- deploy edge service cloudflare workers
---

# Cloudflare Workers, KV, D1 SQL & Durable Objects

## Objective
Build low-latency, globally replicated edge applications with zero server provisioning using Cloudflare Workers, D1 distributed SQL, and persistent Durable Objects.

## Configuration & Edge Worker (`wrangler.toml` & `worker.ts`)
```toml
name = "edge-api-gateway"
main = "src/index.ts"
compatibility_date = "2025-01-01"

[[d1_databases]]
binding = "DB"
database_name = "production-d1"
database_id = "xxxx-xxxx-xxxx"

[[kv_namespaces]]
binding = "CACHE"
id = "yyyy-yyyy-yyyy"
```

```typescript
export interface Env {
  DB: D1Database;
  CACHE: KVNamespace;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/items') {
      # Check edge KV cache
      const cached = await env.CACHE.get('items_list');
      if (cached) {
        return new Response(cached, { headers: { 'Content-Type': 'application/json', 'X-Cache': 'HIT' } });
      }

      # Query D1 Distributed SQLite
      const { results } = await env.DB.prepare('SELECT id, name, price FROM items ORDER BY price ASC LIMIT 50').all();
      const body = JSON.stringify(results);

      await env.CACHE.put('items_list', body, { expirationTtl: 300 });
      return new Response(body, { headers: { 'Content-Type': 'application/json', 'X-Cache': 'MISS' } });
    }

    return new Response('Not Found', { status: 404 });
  },
};
```

## Anti-Patterns
- ❌ Performing unindexed heavy joins in D1 edge SQLite databases.
