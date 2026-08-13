# Next.js 15 App Router Architecture & Server Actions

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