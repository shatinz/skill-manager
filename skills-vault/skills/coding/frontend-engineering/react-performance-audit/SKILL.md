---
id: coding.frontend-engineering.react-performance-audit
name: react-performance-audit
title: React & Next.js Performance Audit & Optimization
category: coding
subcategory: frontend-engineering
version: 1.2.0
tags:
- react
- nextjs
- performance
- frontend
- web-vitals
- re-render
trust_rating: 0.97
estimated_tokens: 1550
description: Eliminate wasted React re-renders, optimize Core Web Vitals (LCP, INP,
  CLS), implement smart memoization, virtualization for large lists, and dynamic code
  splitting.
trigger_patterns:
- fix react re-renders
- optimize nextjs performance
- audit react performance
- improve core web vitals
- react memo usecallback audit
---

# React & Next.js Performance Audit & Optimization

## Objective
Diagnose and eliminate UI stutter, high Interaction to Next Paint (INP), and redundant component re-render cascades.

## Diagnostic Strategy
1. **React DevTools Profiler**: Record user interaction, filter by 'Why did this render?'.
2. **State Colocation**: Move ephemeral state down to leaf components to isolate re-render boundaries.
3. **List Virtualization**: Use TanStack Virtual for lists exceeding 100 items.
4. **Bundle Splitting**: Replace heavy static imports with `next/dynamic` or `React.lazy`.
