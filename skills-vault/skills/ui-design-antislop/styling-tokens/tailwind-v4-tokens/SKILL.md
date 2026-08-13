---
id: ui-design-antislop.styling-tokens.tailwind-v4-tokens
name: tailwind-v4-tokens
title: Tailwind CSS v4 CSS-First Design Tokens & Theme Craft
category: ui-design-antislop
subcategory: styling-tokens
version: 1.1.0
tags:
- tailwind-v4
- css-variables
- design-tokens
- theme
- oklch
- container-queries
trust_rating: 0.98
estimated_tokens: 1550
description: Configure and structure CSS-first theme tokens in Tailwind CSS v4 using
  @theme directives, OKLCH wide-gamut palettes, dynamic dark mode variables, and container
  queries without javascript config files.
trigger_patterns:
- tailwind v4 theme tokens
- tailwind v4 css @theme directive
- tailwind v4 oklch colors
- tailwind 4 container queries
- migrate to tailwind v4
---

# Tailwind CSS v4 CSS-First Design Tokens & Theme Craft

## Objective
Adopt Tailwind CSS v4's CSS-first architecture using `@theme` blocks, `@utility` definitions, and OKLCH color spaces to build responsive, tokenized design systems with zero JS configuration.

## Key Principles
1. **Zero-JS Config**: `tailwind.config.js` is replaced with standard `@theme` in CSS.
2. **OKLCH Color Space**: Provides perceptually uniform lightness across hues for predictable dark/light mode balance.
3. **Container Query First**: Use `@container` and `@sm`, `@md` container variants for component-driven layout flexibility.

## Production CSS Token Structure (`src/styles/app.css`)
```css
@import "tailwindcss";

@theme {
  --font-sans: 'Inter Variable', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* OKLCH Wide-Gamut Palette */
  --color-brand-50: oklch(0.97 0.02 260);
  --color-brand-500: oklch(0.62 0.22 260);
  --color-brand-600: oklch(0.52 0.24 260);
  --color-brand-900: oklch(0.24 0.12 260);

  --color-surface-base: oklch(0.99 0 0);
  --color-surface-subtle: oklch(0.95 0.01 260);
  --color-surface-elevated: oklch(1.0 0 0);
  --color-border-subtle: oklch(0.90 0.01 260);
  --color-text-primary: oklch(0.18 0.02 260);
  --color-text-secondary: oklch(0.45 0.03 260);

  --radius-subtle: 0.375rem;
  --radius-panel: 0.75rem;
}

@media (prefers-color-scheme: dark) {
  @theme {
    --color-surface-base: oklch(0.14 0.02 260);
    --color-surface-subtle: oklch(0.18 0.03 260);
    --color-surface-elevated: oklch(0.22 0.03 260);
    --color-border-subtle: oklch(0.28 0.03 260);
    --color-text-primary: oklch(0.96 0.01 260);
    --color-text-secondary: oklch(0.72 0.02 260);
  }
}

@utility glass-panel {
  background-color: oklch(from var(--color-surface-elevated) l c h / 0.75);
  backdrop-filter: blur(12px);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-panel);
}
```

## Anti-Patterns
- ❌ Hardcoding arbitrary hex codes (`#1a202c`) inside classes instead of utilizing semantic theme tokens.
- ❌ Retaining legacy JavaScript config files (`tailwind.config.js`) in fresh Tailwind v4 projects.
