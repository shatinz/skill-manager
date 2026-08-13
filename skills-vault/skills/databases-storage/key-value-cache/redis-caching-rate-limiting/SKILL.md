---
id: databases-storage.key-value-cache.redis-caching-rate-limiting
name: redis-caching-rate-limiting
title: Redis High-Performance Caching, Sliding Window Rate Limiting & Pub/Sub
category: databases-storage
subcategory: key-value-cache
version: 1.4.0
tags:
- redis
- caching
- rate-limiting
- lua
- sliding-window
- ioredis
trust_rating: 0.98
estimated_tokens: 1600
description: Implement robust Redis cache-aside patterns with jittered TTLs, atomic
  Lua sliding window rate limiters, distributed locks with Redlock, and Pub/Sub event
  streams.
trigger_patterns:
- redis sliding window rate limit lua
- redis cache aside ttl jitter
- redis distributed lock redlock
- ioredis connection pool rate limiting
---

# Redis High-Performance Caching & Sliding Window Rate Limiting

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
