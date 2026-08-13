---
id: ui-design-antislop.component-systems.shadcn-ui-mastery
name: shadcn-ui-mastery
title: shadcn/ui Component Composition & Radix Primitives
category: ui-design-antislop
subcategory: component-systems
version: 1.3.0
tags:
- shadcn-ui
- radix-ui
- cva
- tailwind
- accessibility
- react
trust_rating: 0.99
estimated_tokens: 1600
description: Compose accessible, customizable design systems using shadcn/ui patterns,
  Radix UI unstyled primitives, Class Variance Authority (CVA), and the cn() tailwind-merge
  helper.
trigger_patterns:
- shadcn ui component composition
- radix ui accessibility shadcn
- class variance authority cva button
- cn tailwind merge clsx helper
---

# shadcn/ui Component Composition & Radix Primitives

## Objective
Build fully accessible (WAI-ARIA compliant), theme-ready component architectures using shadcn/ui composition principles with CVA variants and polymorphic `asChild` Radix slots.

## Production Blueprint (`components/ui/button.tsx`)
```tsx
import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground shadow hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90',
        outline: 'border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-9 px-4 py-2',
        sm: 'h-8 rounded-md px-3 text-xs',
        lg: 'h-10 rounded-md px-8',
        icon: 'h-9 w-9',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';
```

## Anti-Patterns
- ❌ Overriding styles with `!important` instead of passing clean class overrides merged via `cn()`.
- ❌ Breaking keyboard accessibility by replacing Radix Dialog/Dropdown with manual click-toggle state divs.
