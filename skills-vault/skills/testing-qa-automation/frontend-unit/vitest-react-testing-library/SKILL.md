---
id: testing-qa-automation.frontend-unit.vitest-react-testing-library
name: vitest-react-testing-library
title: Vitest & React Testing Library (RTL) Component Testing
category: testing-qa-automation
subcategory: frontend-unit
version: 1.3.0
tags:
- vitest
- react-testing-library
- rtl
- user-event
- jsdom
- unit-testing
trust_rating: 0.97
estimated_tokens: 1500
description: Author lightning-fast React component unit tests using Vitest, React
  Testing Library, user-event interactions, and accessibility-first queries.
trigger_patterns:
- vitest react testing library setup
- test react component user-event
- rtl getByRole accessibility queries
- mock service worker msw vitest
---

# Vitest & React Testing Library Component Testing

## Objective
Deliver rapid, high-confidence React component unit tests by verifying user-facing accessibility behavior rather than component internal implementation details.

## Blueprint (`src/components/Modal.test.tsx`)
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { ConfirmationModal } from './ConfirmationModal';

describe('ConfirmationModal Component', () => {
  it('calls onConfirm when user clicks the confirm button', async () => {
    const user = userEvent.setup();
    const handleConfirm = vi.fn();

    render(
      <ConfirmationModal
        isOpen={true}
        title="Delete Item"
        onConfirm={handleConfirm}
        onCancel={() => {}}
      />
    );

    expect(screen.getByRole('heading', { name: /delete item/i })).toBeInTheDocument();
    
    const confirmBtn = screen.getByRole('button', { name: /confirm/i });
    await user.click(confirmBtn);

    expect(handleConfirm).toHaveBeenCalledTimes(1);
  });
});
```

## Anti-Patterns
- ❌ Testing internal state variables (`wrapper.state()`) instead of rendered DOM output.
