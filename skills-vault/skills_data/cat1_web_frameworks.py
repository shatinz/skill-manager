"""
Category 1: Web Frameworks (7 Skills)
"""

WEB_FRAMEWORKS_SKILLS = [
    {
        "id": "web-frameworks.react-fullstack.nextjs-15-app-router",
        "name": "nextjs-15-app-router",
        "title": "Next.js 15 App Router Architecture & Server Actions",
        "category": "web-frameworks",
        "subcategory": "react-fullstack",
        "version": "1.5.0",
        "tags": ["nextjs", "react-19", "server-actions", "app-router", "typescript", "rsc", "turbopack"],
        "trust_rating": 0.99,
        "estimated_tokens": 1750,
        "description": "Architect, implement, and optimize Next.js 15 fullstack applications using React Server Components, Server Actions, async request APIs (cookies, headers, params), granular cache revalidation, and streaming suspense boundaries.",
        "trigger_patterns": [
            "build nextjs 15 app",
            "nextjs 15 server actions",
            "react server components rsc nextjs",
            "nextjs 15 cache revalidateTag",
            "nextjs app router nested layouts",
            "nextjs async cookies headers"
        ],
        "content": """# Next.js 15 App Router Architecture & Server Actions

## Objective
Build high-performance, SEO-optimized, secure web applications leveraging Next.js 15 (React 19), React Server Components (RSC), asynchronous request APIs, typed Server Actions, and granular tag-based cache revalidation.

## Architectural Principles
1. **Server-First by Default**: Keep all components as React Server Components (RSC) unless interactivity, browser APIs, or React client hooks (`useState`, `useEffect`, `useActionState`) are strictly required.
2. **Async Request Lifecycle**: In Next.js 15, `cookies()`, `headers()`, `params`, and `searchParams` are asynchronous promises. Always await them: `const params = await props.params;`.
3. **Safe Server Actions**: Validate all action inputs with Zod schemas. Enforce user authorization inside the action before mutations. Use `useActionState` and `useFormStatus` on the client for optimistic feedback.
4. **Granular Revalidation**: Prefer `revalidateTag(tag)` over blunt `revalidatePath()`. Wrap non-critical data fetches in `<Suspense fallback={<Skeleton />}>` for instant TTFB.

## Production Blueprint

### 1. Type-Safe Server Action with Zod (`actions/items.ts`)
```typescript
'use server';

import { z } from 'zod';
import { revalidateTag } from 'next/cache';
import { auth } from '@/lib/auth';
import { db } from '@/lib/db';

const CreateItemSchema = z.object({
  title: z.string().min(3).max(120),
  description: z.string().max(500).optional(),
  price: z.coerce.number().positive(),
});

export type ActionState = {
  success?: boolean;
  message?: string;
  errors?: Record<string, string[]>;
};

export async function createItemAction(
  prevState: ActionState,
  formData: FormData
): Promise<ActionState> {
  const session = await auth();
  if (!session?.user?.id) {
    return { success: false, message: 'Unauthorized. Please sign in.' };
  }

  const rawData = Object.fromEntries(formData.entries());
  const validated = CreateItemSchema.safeParse(rawData);

  if (!validated.success) {
    return {
      success: false,
      errors: validated.error.flatten().fieldErrors,
      message: 'Validation failed. Please correct input errors.',
    };
  }

  try {
    await db.item.create({
      data: {
        ...validated.data,
        userId: session.user.id,
      },
    });

    revalidateTag('items-feed');
    return { success: true, message: 'Item created successfully.' };
  } catch (error) {
    console.error('Failed to create item:', error);
    return { success: false, message: 'Internal database error.' };
  }
}
```

### 2. Async Page Component with Suspense (`app/items/[id]/page.tsx`)
```tsx
import { Suspense } from 'react';
import { notFound } from 'next/navigation';
import { getItemById } from '@/lib/data/items';
import { ItemDetailView } from '@/components/item-detail-view';
import { SkeletonCard } from '@/components/ui/skeleton-card';

type PageProps = {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
};

export default async function ItemPage(props: PageProps) {
  const { id } = await props.params;

  return (
    <main className="container mx-auto px-4 py-8">
      <Suspense fallback={<SkeletonCard />}>
        <ItemContent id={id} />
      </Suspense>
    </main>
  );
}

async function ItemContent({ id }: { id: string }) {
  const item = await getItemById(id);
  if (!item) notFound();

  return <ItemDetailView item={item} />;
}
```

## Anti-Patterns to Avoid
- ❌ **Client Component Creep**: Adding `'use client'` at the page or layout level. Instead, push `'use client'` down to the leaves (buttons, interactive forms).
- ❌ **Unawaited Request APIs**: Treating `params` or `cookies()` as synchronous objects in Next.js 15.
- ❌ **Waterfall Fetching**: Cascading `await fetchA()` then `await fetchB()`. Use `Promise.all([fetchA(), fetchB()])` or separate `<Suspense>` streams.
- ❌ **Missing CSRF & Auth**: Exposing server actions without validating caller session and input schemas.

## Verification Checklist
- [ ] Run `npx next lint` and ensure no synchronous params/cookies deprecation warnings.
- [ ] Verify Server Action validation returns structured field errors without throwing unhandled exceptions.
- [ ] Check Network tab to confirm HTML streaming TTFB is under 150ms with `<Suspense>` boundaries.
"""
    },

    {
        "id": "web-frameworks.python-api.fastapi-production-craft",
        "name": "fastapi-production-craft",
        "title": "FastAPI Production Architecture & Async Engineering",
        "category": "web-frameworks",
        "subcategory": "python-api",
        "version": "1.5.0",
        "tags": ["fastapi", "python", "pydantic-v2", "asyncio", "sqlalchemy-async", "openapi", "rfc7807"],
        "trust_rating": 0.98,
        "estimated_tokens": 1650,
        "description": "Architect, implement, and harden production-grade FastAPI REST and async services with Pydantic v2 schemas, SQLAlchemy 2.0 async sessions, dependency injection, and standardized RFC 7807 error envelopes.",
        "trigger_patterns": [
            "create fastapi backend",
            "fastapi production setup",
            "fastapi async sqlalchemy 2",
            "pydantic v2 fastapi schemas",
            "fastapi dependency injection lifespan",
            "fastapi rfc7807 error handling"
        ],
        "content": """# FastAPI Production Architecture & Async Engineering

## Objective
Design high-throughput, maintainable, and type-safe async REST APIs using FastAPI, Pydantic v2, and SQLAlchemy 2.0 with clean layered architecture (Routers -> Services -> Repositories -> Models).

## Architectural Guidelines
1. **Layered Structure**: Routers handle HTTP parsing, status codes, and dependency injection. Services handle business logic and orchestration. Repositories handle database I/O.
2. **Lifespan Context**: Use `@asynccontextmanager` lifespan handlers for startup/shutdown (connection pools, Redis, Kafka clients) instead of deprecated `on_event`.
3. **Pydantic v2 Strictness**: Use `model_validate`, `model_dump`, and `ConfigDict(from_attributes=True)` for serialization.
4. **RFC 7807 Problem Details**: Structure all error responses with `type`, `title`, `status`, `detail`, and `instance`.

## Production Blueprint

### Service Layer & Router (`routers/orders.py`)
```python
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import uuid

# Lifespan and Engine
DATABASE_URL = "postgresql+asyncpg://postgres:secret@localhost:5432/appdb"
engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=10)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

DbSession = Annotated[AsyncSession, Depends(get_db_session)]

# Schemas
class OrderCreate(BaseModel):
    customer_email: str = Field(..., max_length=255)
    sku: str = Field(..., min_length=3, max_length=50)
    quantity: int = Field(1, ge=1, le=100)

class OrderResponse(BaseModel):
    id: uuid.UUID
    customer_email: str
    sku: str
    quantity: int
    status: str
    model_config = ConfigDict(from_attributes=True)

# Router
router = APIRouter(prefix="/v1/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, db: DbSession):
    order = await order_service.place_order(db=db, payload=payload)
    return order

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: uuid.UUID, db: DbSession):
    order = await order_service.get_order(db=db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found."
        )
    return order
```

## Anti-Patterns & Traps
- ❌ **Blocking Calls in Async Def**: Running `requests.get()` or `time.sleep()` in `async def` endpoints locks the event loop. Use `httpx.AsyncClient` or `asyncio.sleep`.
- ❌ **Direct ORM Exposure**: Returning SQLAlchemy models without Pydantic conversion causes memory leaks, circular serialization, and secret exposure.
- ❌ **Missing Async Commit/Rollback**: Failing to use session context managers leaves uncommitted transactions dangling in connection pools.

## Verification
- [ ] Execute `pytest-asyncio` test suite with `httpx.AsyncClient(transport=ASGITransport(app=app))` fixture.
- [ ] Profile concurrent throughput with `wrk` or `locust` to verify no event-loop blocking.
"""
    },

    {
        "id": "web-frameworks.svelte.sveltekit-5-runes",
        "name": "sveltekit-5-runes",
        "title": "SvelteKit 5 Runes & Modern Reactive Fullstack Craft",
        "category": "web-frameworks",
        "subcategory": "svelte",
        "version": "1.2.0",
        "tags": ["sveltekit", "svelte-5", "runes", "state", "props", "derived", "typescript"],
        "trust_rating": 0.96,
        "estimated_tokens": 1600,
        "description": "Master SvelteKit 5 runes reactive paradigm ($state, $derived, $effect, $props), server load functions, typed form actions with progressive enhancement, and robust state orchestration.",
        "trigger_patterns": [
            "svelte 5 runes setup",
            "sveltekit 5 $state $derived",
            "sveltekit 5 form actions enhance",
            "svelte 5 props runes migration",
            "sveltekit server load function"
        ],
        "content": """# SvelteKit 5 Runes & Modern Reactive Fullstack Craft

## Objective
Build reactive, lightweight, fullstack web applications using SvelteKit 5, utilizing the modern Runes reactive system (`$state`, `$derived`, `$effect`, `$props`, `$bindable`), universal/server load functions, and progressively enhanced form actions.

## Core Runes Paradigm
1. **Explicit Reactivity**: Svelte 5 replaces `let x = 1` and `$: doubled = x * 2` with explicit runes `$state(1)` and `$derived(x * 2)`.
2. **Component Props**: Receive props with `let { propA, propB = 'default' }: Props = $props();`.
3. **Form Actions**: Handle form submissions in `+page.server.ts` with `actions`, enhanced on the client via `use:enhance`.

## Production Blueprint

### 1. Svelte 5 Component with Runes (`src/lib/components/CounterCart.svelte`)
```svelte
<script lang="ts">
  interface CartItem {
    id: string;
    name: string;
    price: number;
    qty: number;
  }

  interface Props {
    initialItems?: CartItem[];
    currency?: string;
    onCheckout?: (total: number) => void;
  }

  let { initialItems = [], currency = '$', onCheckout }: Props = $props();

  // Reactive State
  let items = $state<CartItem[]>(initialItems);

  // Derived State
  let totalCount = $derived(items.reduce((sum, item) => sum + item.qty, 0));
  let totalPrice = $derived(items.reduce((sum, item) => sum + item.price * item.qty, 0));

  function updateQty(id: string, delta: number) {
    const item = items.find((i) => i.id === id);
    if (item) {
      item.qty = Math.max(0, item.qty + delta);
    }
  }

  // Side-effect Rune
  $effect(() => {
    if (totalCount > 10) {
      console.log('Bulk discount eligible!');
    }
  });
</script>

<div class="cart-container p-6 bg-slate-900 text-white rounded-xl">
  <h2 class="text-xl font-bold mb-4">Cart Summary ({totalCount} items)</h2>
  
  {#each items as item (item.id)}
    <div class="flex justify-between items-center py-2 border-b border-slate-800">
      <span>{item.name} ({currency}{item.price})</span>
      <div class="flex items-center gap-2">
        <button class="px-2 py-1 bg-slate-700 rounded" onclick={() => updateQty(item.id, -1)}>-</button>
        <span class="w-8 text-center">{item.qty}</span>
        <button class="px-2 py-1 bg-slate-700 rounded" onclick={() => updateQty(item.id, 1)}>+</button>
      </div>
    </div>
  {/each}

  <div class="mt-4 flex justify-between items-center font-bold text-lg">
    <span>Total:</span>
    <span>{currency}{totalPrice.toFixed(2)}</span>
  </div>

  <button
    class="w-full mt-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded font-semibold transition"
    onclick={() => onCheckout?.(totalPrice)}
  >
    Proceed to Checkout
  </button>
</div>
```

### 2. Server Load & Form Actions (`src/routes/cart/+page.server.ts`)
```typescript
import type { PageServerLoad, Actions } from './$types';
import { fail } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ locals }) => {
  return {
    user: locals.user,
    cartItems: [
      { id: '1', name: 'Agent Skill Vault Pass', price: 49, qty: 1 }
    ]
  };
};

export const actions: Actions = {
  checkout: async ({ request, locals }) => {
    const data = await request.formData();
    const total = Number(data.get('total'));

    if (!total || isNaN(total)) {
      return fail(400, { message: 'Invalid total price' });
    }

    return { success: true, transactionId: crypto.randomUUID() };
  }
};
```

## Anti-Patterns
- ❌ **Legacy Svelte 3/4 Syntax**: Mixing `$: doubled = ...` with `$state()`.
- ❌ **Mutating $state in $derived**: `$derived` must remain pure calculations without state mutations.
- ❌ **Direct DOM Mutation in $effect**: Avoid manual querySelector inside `$effect`; rely on Svelte template bindings.

## Verification
- [ ] Run `npm run check` (svelte-check) with TypeScript in strict mode.
- [ ] Verify reactive rune reactivity persists across nested property updates.
"""
    },

    {
        "id": "web-frameworks.edge-runtime.hono-edge-api",
        "name": "hono-edge-api",
        "title": "Hono Ultra-Fast Edge & Multi-Runtime API Craft",
        "category": "web-frameworks",
        "subcategory": "edge-runtime",
        "version": "1.3.0",
        "tags": ["hono", "cloudflare-workers", "deno", "bun", "edge", "typescript", "zod-validator", "rpc"],
        "trust_rating": 0.97,
        "estimated_tokens": 1550,
        "description": "Construct high-performance, edge-first API services using Hono with full TypeScript inference, Zod request validation middleware, RPC client generation, and multi-runtime portability.",
        "trigger_patterns": [
            "create hono edge api",
            "hono cloudflare workers setup",
            "hono zod validator rpc",
            "hono typed middleware",
            "fast lightweight edge router hono"
        ],
        "content": """# Hono Ultra-Fast Edge & Multi-Runtime API Craft

## Objective
Build microsecond-latency, multi-runtime APIs deployable to Cloudflare Workers, Fastly, Deno, Bun, or Node.js using Hono with typed RPC client generation and Zod validation.

## Architectural Principles
1. **Multi-Runtime Core**: Standard Web Standards (`Request`, `Response`, `fetch`, `Streams`). Avoid Node-specific internals unless isolated in adapters.
2. **End-to-End Type Safety (RPC)**: Export `type AppType = typeof routes` and consume via `hc<AppType>()` on the frontend for zero-codegen typed RPC.
3. **Structured Validation**: Use `@hono/zod-validator` for `json`, `query`, `param`, and `header` schemas.

## Production Blueprint

### Edge API Implementation (`src/index.ts`)
```typescript
import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import { z } from 'zod';
import { cors } from 'hono/cors';
import { secureHeaders } from 'hono/secure-headers';

type Bindings = {
  KV_STORE: KVNamespace;
  AUTH_SECRET: string;
};

type Variables = {
  userId: string;
};

const app = new Hono<{ Bindings: Bindings; Variables: Variables }>();

// Security Middlewares
app.use('*', secureHeaders());
app.use('/api/*', cors({ origin: ['https://example.com'], allowMethods: ['GET', 'POST'] }));

// Validation Schemas
const CreateWebhookSchema = z.object({
  targetUrl: z.string().url(),
  events: z.array(z.string()).min(1),
  secret: z.string().min(16),
});

// Chained Typed Routes
const routes = app
  .post(
    '/api/v1/webhooks',
    zValidator('json', CreateWebhookSchema),
    async (c) => {
      const data = c.req.valid('json');
      const webhookId = crypto.randomUUID();

      // Write to Cloudflare KV Edge storage
      await c.env.KV_STORE.put(`webhook:${webhookId}`, JSON.stringify(data), {
        expirationTtl: 86400 * 30, // 30 days
      });

      return c.json(
        {
          id: webhookId,
          status: 'active',
          targetUrl: data.targetUrl,
          createdAt: new Date().toISOString(),
        },
        201
      );
    }
  )
  .get('/api/v1/webhooks/:id', async (c) => {
    const id = c.req.param('id');
    const record = await c.env.KV_STORE.get(`webhook:${id}`);
    
    if (!record) {
      return c.json({ error: 'Webhook subscription not found' }, 404);
    }

    return c.json({ id, data: JSON.parse(record) });
  });

export type AppType = typeof routes;
export default app;
```

### Type-Safe Frontend Client (`client.ts`)
```typescript
import { hc } from 'hono/client';
import type { AppType } from './index';

const client = hc<AppType>('https://api.example.com');

async function triggerRegistration() {
  const res = await client.api.v1.webhooks.$post({
    json: {
      targetUrl: 'https://myservice.io/events',
      events: ['user.created', 'order.paid'],
      secret: 'secret_entropy_12345',
    },
  });

  if (res.ok) {
    const payload = await res.json();
    console.log('Created webhook:', payload.id);
  }
}
```

## Anti-Patterns
- ❌ **Mixing Node.js fs/crypto APIs**: Rely on Web Crypto API (`crypto.subtle`, `crypto.randomUUID()`) for cross-runtime compatibility.
- ❌ **Unbuffered Large Payloads**: Parsing multi-MB payloads into memory simultaneously on edge workers with 128MB RAM caps.

## Verification
- [ ] Test locally using `wrangler dev` or `bun run index.ts`.
- [ ] Confirm client RPC compilation has zero TypeScript errors and validates response shapes.
"""
    },

    {
        "id": "web-frameworks.react-fullstack.remix-fullstack-patterns",
        "name": "remix-fullstack-patterns",
        "title": "Remix & React Router v7 Fullstack Patterns",
        "category": "web-frameworks",
        "subcategory": "react-fullstack",
        "version": "1.2.0",
        "tags": ["remix", "react-router-v7", "loader", "action", "optimistic-ui", "typescript"],
        "trust_rating": 0.95,
        "estimated_tokens": 1500,
        "description": "Design resilient fullstack applications with Remix and React Router v7 loaders, actions, optimistic UI with useFetcher, nested error boundaries, and streaming defer responses.",
        "trigger_patterns": [
            "remix loader action patterns",
            "react router v7 fullstack setup",
            "remix optimistic ui useFetcher",
            "remix defer streaming suspense"
        ],
        "content": """# Remix & React Router v7 Fullstack Patterns

## Objective
Structure robust web apps using standard Web API loaders, mutations via actions, automatic cache invalidation, and optimistic state updates without client-side state managers.

## Key Patterns
1. **Loaders (Data Providers)**: Run exclusively on the server to supply data to routes before rendering.
2. **Actions (Mutations)**: HTML Form-first mutations that automatically revalidate all active loaders upon completion.
3. **Optimistic UI with `useFetcher`**: Render changes immediately using `fetcher.formData` while the network mutation resolves in the background.

## Production Blueprint

```tsx
import type { LoaderFunctionArgs, ActionFunctionArgs } from '@remix-run/node';
import { json } from '@remix-run/node';
import { useLoaderData, useFetcher } from '@remix-run/react';
import { db } from '~/lib/db.server';

export async function loader({ request }: LoaderFunctionArgs) {
  const todos = await db.todo.findMany({ orderBy: { createdAt: 'desc' } });
  return json({ todos });
}

export async function action({ request }: ActionFunctionArgs) {
  const formData = await request.formData();
  const intent = formData.get('intent');

  if (intent === 'toggle') {
    const id = String(formData.get('id'));
    const completed = formData.get('completed') === 'true';
    await db.todo.update({ where: { id }, data: { completed } });
    return json({ ok: true });
  }

  return json({ error: 'Unknown action' }, { status: 400 });
}

export default function TodoRoute() {
  const { todos } = useLoaderData<typeof loader>();
  const fetcher = useFetcher();

  return (
    <ul className="space-y-2 p-6">
      {todos.map((todo) => {
        const isOptimisticToggle =
          fetcher.formData?.get('id') === todo.id &&
          fetcher.formData?.get('intent') === 'toggle';
        
        const isCompleted = isOptimisticToggle
          ? fetcher.formData?.get('completed') === 'true'
          : todo.completed;

        return (
          <li key={todo.id} className="flex items-center gap-3">
            <fetcher.Form method="post">
              <input type="hidden" name="intent" value="toggle" />
              <input type="hidden" name="id" value={todo.id} />
              <input
                type="checkbox"
                name="completed"
                value={isCompleted ? 'false' : 'true'}
                checked={isCompleted}
                onChange={(e) => e.currentTarget.form?.requestSubmit()}
              />
            </fetcher.Form>
            <span className={isCompleted ? 'line-through text-gray-500' : 'text-gray-900'}>
              {todo.title}
            </span>
          </li>
        );
      })}
    </ul>
  );
}
```

## Anti-Patterns & Verification
- ❌ Do NOT use client `useEffect` for data fetching; use route `loader`.
- ❌ Do NOT manually re-fetch data after mutation; Remix actions automatically re-execute matching active loaders.
"""
    },

    {
        "id": "web-frameworks.content-ssg.astro-content-collections",
        "name": "astro-content-collections",
        "title": "Astro Content Collections & Islands Architecture",
        "category": "web-frameworks",
        "subcategory": "content-ssg",
        "version": "1.3.0",
        "tags": ["astro", "content-collections", "islands", "zod", "ssg", "mdx", "performance"],
        "trust_rating": 0.97,
        "estimated_tokens": 1450,
        "description": "Construct blazing-fast content-driven static and hybrid websites with Astro 5 Content Collections, strict Zod schema validation, and selective island hydration.",
        "trigger_patterns": [
            "astro content collections zod",
            "astro islands architecture hydration",
            "astro mdx blog static site",
            "astro client:load client:visible"
        ],
        "content": """# Astro Content Collections & Islands Architecture

## Objective
Build zero-JavaScript-by-default websites using Astro 5 Content Layer, Markdown/MDX type-safety, and selective client component hydration (`client:load`, `client:visible`).

## Content Layer Schema (`src/content.config.ts`)
```typescript
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/data/blog' }),
  schema: ({ image }) =>
    z.object({
      title: z.string().max(80),
      description: z.string(),
      pubDate: z.coerce.date(),
      coverImage: image().optional(),
      tags: z.array(z.string()).default([]),
      draft: z.boolean().default(false),
    }),
});

export const collections = { blog };
```

## Dynamic Static Page (`src/pages/blog/[slug].astro`)
```astro
---
import { getCollection, render } from 'astro:content';
import BaseLayout from '../../layouts/BaseLayout.astro';
import InteractiveComments from '../../components/InteractiveComments.tsx';

export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  return posts.map((post) => ({
    params: { slug: post.id },
    props: { post },
  }));
}

const { post } = Astro.props;
const { Content } = await render(post);
---

<BaseLayout title={post.data.title}>
  <article class="prose max-w-3xl mx-auto py-12">
    <h1>{post.data.title}</h1>
    <time>{post.data.pubDate.toLocaleDateString()}</time>
    <Content />
    
    <!-- Island hydrated only when scrolled into view -->
    <InteractiveComments client:visible postId={post.id} />
  </article>
</BaseLayout>
```

## Anti-Patterns
- ❌ Hydrating entire page headers/footers with `client:load` when pure static HTML suffices.
- ❌ Bypassing Content Collections with raw filesystem reads.
"""
    },

    {
        "id": "web-frameworks.python-api.django-ninja-crud",
        "name": "django-ninja-crud",
        "title": "Django Ninja Type-Safe Async REST & Schema Craft",
        "category": "web-frameworks",
        "subcategory": "python-api",
        "version": "1.2.0",
        "tags": ["django-ninja", "django", "pydantic", "async", "rest-api", "python"],
        "trust_rating": 0.94,
        "estimated_tokens": 1400,
        "description": "Build high-speed, type-safe REST APIs in Django using Django Ninja with Pydantic schemas, async ORM queries, authentication guards, and automatic OpenAPI generation.",
        "trigger_patterns": [
            "django ninja rest api",
            "django ninja async crud",
            "django ninja pydantic schemas",
            "django ninja auth tokens"
        ],
        "content": """# Django Ninja Type-Safe Async REST & Schema Craft

## Objective
Develop type-safe, high-performance REST APIs within the Django ecosystem utilizing Django Ninja, Pydantic schemas, and asynchronous querysets.

## Blueprint (`api/views.py`)
```python
from ninja import NinjaAPI, Schema, ModelSchema
from ninja.pagination import paginate, PageNumberPagination
from ninja.security import HttpBearer
from typing import List
from django.shortcuts import aget_object_or_404
from .models import Product

api = NinjaAPI(title="Commerce Engine API", version="1.0.0")

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token == "super-secret-token":
            return {"username": "admin_agent"}
        return None

class ProductIn(Schema):
    title: str
    price: float
    sku: str
    in_stock: bool = True

class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'sku', 'in_stock', 'created_at']

@api.get("/products", response=List[ProductOut])
@paginate(PageNumberPagination, page_size=20)
async def list_products(request):
    return [p async for p in Product.objects.filter(in_stock=True).order_by('-created_at')]

@api.post("/products", response={201: ProductOut}, auth=AuthBearer())
async def create_product(request, payload: ProductIn):
    product = await Product.objects.acreate(**payload.dict())
    return 201, product
```

## Anti-Patterns
- ❌ Running synchronous ORM queries inside `async def` endpoints without `sync_to_async` or async ORM helpers (`acreate`, `aget_object_or_404`).
"""
    },

    {
        "id": "web-frameworks.react-fullstack.tanstack-query-router-modern",
        "name": "tanstack-query-router-modern",
        "title": "TanStack Router & Query v5 Type-Safe Fullstack Architecture",
        "category": "web-frameworks",
        "subcategory": "react-fullstack",
        "version": "1.3.0",
        "tags": ["tanstack-router", "tanstack-query", "react", "type-safety", "loaders", "cache-invalidation", "ssr"],
        "trust_rating": 0.99,
        "estimated_tokens": 1900,
        "description": "Construct 100% type-safe single-page and SSR web applications with TanStack Router, TanStack Query v5, search parameter schemas with Zod, route loaders, and automatic cache invalidation.",
        "trigger_patterns": [
            "tanstack router type safe routes",
            "tanstack query v5 loader prefetching",
            "tanstack router search params zod validation",
            "tanstack router createRoute queryClient"
        ],
        "content": """# TanStack Router & Query v5 Type-Safe Fullstack Architecture

## Objective
Build resilient, 100% type-safe client-side and SSR applications using TanStack Router for route tree definition, search parameter validation, and parallel data prefetching with TanStack Query v5.

## Route Definition (`src/routes/posts.$postId.tsx`)
```typescript
import { createFileRoute } from '@tanstack/react-router';
import { queryOptions, useSuspenseQuery } from '@tanstack/react-query';
import { z } from 'zod';

// 1. Define Query Options
export const postQueryOptions = (postId: string) =>
  queryOptions({
    queryKey: ['posts', postId],
    queryFn: async () => {
      const res = await fetch(`/api/posts/${postId}`);
      if (!res.ok) throw new Error('Post not found');
      return res.json() as Promise<{ id: string; title: string; body: string }>;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes fresh
  });

// 2. Validate URL Search Parameters with Zod
const searchSchema = z.object({
  tab: z.enum(['details', 'comments', 'history']).default('details'),
  highlight: z.string().optional(),
});

// 3. Create Type-Safe Route with Pre-load Loader
export const Route = createFileRoute('/posts/$postId')({
  validateSearch: searchSchema,
  loader: ({ context: { queryClient }, params: { postId } }) =>
    queryClient.ensureQueryData(postQueryOptions(postId)),
  component: PostDetailComponent,
});

function PostDetailComponent() {
  const { postId } = Route.useParams();
  const search = Route.useSearch();
  const { data: post } = useSuspenseQuery(postQueryOptions(postId));

  return (
    <article className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold">{post.title}</h1>
      <p className="mt-4 text-gray-700 leading-relaxed">{post.body}</p>
      <div className="mt-6 border-t pt-4">
        Active Tab: <strong className="capitalize">{search.tab}</strong>
      </div>
    </article>
  );
}
```

## Golden Rules
1. **Always prefetch in `loader`**: Use `queryClient.ensureQueryData(options)` inside route `loader` to eliminate waterfall network requests.
2. **Validate all search params with Zod**: Prevents invalid URL state crashes.
"""
    },

    {
        "id": "web-frameworks.react-fullstack.react-19-actions-suspense",
        "name": "react-19-actions-suspense",
        "title": "React 19 Server Actions, useActionState & Optimistic UI",
        "category": "web-frameworks",
        "subcategory": "react-fullstack",
        "version": "1.2.0",
        "tags": ["react-19", "server-actions", "useActionState", "useOptimistic", "suspense", "forms"],
        "trust_rating": 0.98,
        "estimated_tokens": 1800,
        "description": "Master React 19 async form actions, progressive enhancement, useActionState, useOptimistic updates, and Suspense boundaries for zero-flicker interactive web apps.",
        "trigger_patterns": [
            "react 19 server actions useActionState",
            "react 19 useOptimistic form submission",
            "react 19 async transitions formStatus",
            "react 19 progressive enhancement forms"
        ],
        "content": """# React 19 Server Actions, useActionState & Optimistic UI

## Objective
Implement clean, state-of-the-art React 19 interactive patterns using native Server Actions, `useActionState` for form state cycles, `useOptimistic` for instant perceived performance, and progressive enhancement.

## Production Form Component (`src/components/AddCommentForm.tsx`)
```tsx
'use client';

import { useActionState, useOptimistic, useRef } from 'react';
import { addCommentAction, CommentState } from '@/actions/comments';

interface Comment {
  id: string;
  author: string;
  text: string;
  sending?: boolean;
}

export function CommentFeed({ initialComments }: { initialComments: Comment[] }) {
  const formRef = useRef<HTMLFormElement>(null);

  // 1. React 19 Action State Hook
  const [state, formAction, isPending] = useActionState<CommentState, FormData>(
    async (prevState, formData) => {
      const text = formData.get('comment') as string;
      // Trigger optimistic preview
      addOptimisticComment(text);
      const res = await addCommentAction(prevState, formData);
      if (res.success) formRef.current?.reset();
      return res;
    },
    { success: false, error: null }
  );

  // 2. React 19 Optimistic UI Hook
  const [optimisticComments, addOptimisticComment] = useOptimistic(
    initialComments,
    (state, newText: string) => [
      ...state,
      { id: Math.random().toString(), author: 'You (Current User)', text: newText, sending: true }
    ]
  );

  return (
    <div className="space-y-6">
      <ul className="space-y-3">
        {optimisticComments.map((c) => (
          <li key={c.id} className={`p-4 rounded-lg bg-gray-50 ${c.sending ? 'opacity-50 italic' : ''}`}>
            <span className="font-semibold text-sm">{c.author}: </span>
            <span>{c.text}</span>
            {c.sending && <span className="text-xs text-blue-500 ml-2">Sending...</span>}
          </li>
        ))}
      </ul>

      <form ref={formRef} action={formAction} className="flex gap-2">
        <input
          name="comment"
          required
          placeholder="Write a comment..."
          className="flex-1 px-4 py-2 border rounded-md"
        />
        <button
          type="submit"
          disabled={isPending}
          className="px-5 py-2 bg-black text-white rounded-md disabled:opacity-50"
        >
          {isPending ? 'Posting...' : 'Post Comment'}
        </button>
      </form>
      {state.error && <p className="text-red-500 text-sm">{state.error}</p>}
    </div>
  );
}
```

## Anti-Patterns
- ❌ Re-inventing manual `useState(loading)` and `useState(error)` spinners when `useActionState` manages the entire async action cycle cleanly.
"""
    }
]

