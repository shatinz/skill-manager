---
id: web-frameworks.react-fullstack.react-19-actions-suspense
name: react-19-actions-suspense
title: React 19 Server Actions, useActionState & Optimistic UI
category: web-frameworks
subcategory: react-fullstack
version: 1.2.0
tags:
- react-19
- server-actions
- useActionState
- useOptimistic
- suspense
- forms
trust_rating: 0.98
estimated_tokens: 1800
description: Master React 19 async form actions, progressive enhancement, useActionState,
  useOptimistic updates, and Suspense boundaries for zero-flicker interactive web
  apps.
trigger_patterns:
- react 19 server actions useActionState
- react 19 useOptimistic form submission
- react 19 async transitions formStatus
- react 19 progressive enhancement forms
---

# React 19 Server Actions, useActionState & Optimistic UI

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
