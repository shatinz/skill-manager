---
id: web-frameworks.svelte.sveltekit-5-runes
name: sveltekit-5-runes
title: SvelteKit 5 Runes & Modern Reactive Fullstack Craft
category: web-frameworks
subcategory: svelte
version: 1.2.0
tags:
- sveltekit
- svelte-5
- runes
- state
- props
- derived
- typescript
trust_rating: 0.96
estimated_tokens: 1600
description: Master SvelteKit 5 runes reactive paradigm ($state, $derived, $effect,
  $props), server load functions, typed form actions with progressive enhancement,
  and robust state orchestration.
trigger_patterns:
- svelte 5 runes setup
- sveltekit 5 $state $derived
- sveltekit 5 form actions enhance
- svelte 5 props runes migration
- sveltekit server load function
---

# SvelteKit 5 Runes & Modern Reactive Fullstack Craft

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
