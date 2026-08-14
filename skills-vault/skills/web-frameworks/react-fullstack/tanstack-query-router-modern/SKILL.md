---
id: web-frameworks.react-fullstack.tanstack-query-router-modern
name: tanstack-query-router-modern
title: TanStack Router & Query v5 Type-Safe Fullstack Architecture
category: web-frameworks
subcategory: react-fullstack
version: 1.3.0
tags:
- tanstack-router
- tanstack-query
- react
- type-safety
- loaders
- cache-invalidation
- ssr
trust_rating: 0.99
estimated_tokens: 1900
description: Construct 100% type-safe single-page and SSR web applications with TanStack
  Router, TanStack Query v5, search parameter schemas with Zod, route loaders, and
  automatic cache invalidation.
trigger_patterns:
- tanstack router type safe routes
- tanstack query v5 loader prefetching
- tanstack router search params zod validation
- tanstack router createRoute queryClient
---

# TanStack Router & Query v5 Type-Safe Fullstack Architecture

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
