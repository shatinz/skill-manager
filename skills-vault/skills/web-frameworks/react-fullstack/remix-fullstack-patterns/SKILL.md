---
id: web-frameworks.react-fullstack.remix-fullstack-patterns
name: remix-fullstack-patterns
title: Remix & React Router v7 Fullstack Patterns
category: web-frameworks
subcategory: react-fullstack
version: 1.2.0
tags:
- remix
- react-router-v7
- loader
- action
- optimistic-ui
- typescript
trust_rating: 0.95
estimated_tokens: 1500
description: Design resilient fullstack applications with Remix and React Router v7
  loaders, actions, optimistic UI with useFetcher, nested error boundaries, and streaming
  defer responses.
trigger_patterns:
- remix loader action patterns
- react router v7 fullstack setup
- remix optimistic ui useFetcher
- remix defer streaming suspense
---

# Remix & React Router v7 Fullstack Patterns

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
