---
id: clean-architecture-refactoring.code-modernization.legacy-code-modernizer
name: legacy-code-modernizer
title: Legacy Code Modernization, Characterization Tests & Strangler Pattern
category: clean-architecture-refactoring
subcategory: code-modernization
version: 1.3.0
tags:
- refactoring
- legacy-code
- strangler-pattern
- characterization-tests
- technical-debt
trust_rating: 0.98
estimated_tokens: 1600
description: Modernize legacy systems safely using the Strangler Fig pattern, characterization
  testing, incremental seams, and automated type enrichment.
trigger_patterns:
- refactor legacy codebase strangler pattern
- characterization tests legacy code
- incremental modernization technical debt
- safely rewrite legacy monolith
---

# Legacy Code Modernization & Strangler Fig Pattern

## Objective
Incrementally decommission legacy codebases without risky big-bang rewrites using the Strangler Fig pattern, golden-master characterization tests, and strict interface seams.

## Step-by-Step Modernization Strategy
1. **Characterization Tests**: Capture current legacy behavior with golden-master snapshot tests before altering a single line.
2. **Identify Seams**: Isolate entry and exit points in the legacy subsystem.
3. **Strangler Proxy**: Route a small percentage of production traffic to the modernized service, comparing results in shadow mode before full cutover.

## Anti-Patterns
- ❌ Attempting full 'Big-Bang' rewrites that halt business delivery for months and fail in production cutovers.
- ❌ Refactoring complex legacy logic without golden master characterization tests.
