---
id: coding.refactoring-clean-code.legacy-code-modernizer
name: legacy-code-modernizer
title: Legacy Codebase Modernizer & Decoupling
category: coding
subcategory: refactoring-clean-code
version: 1.2.0
tags:
- refactoring
- clean-code
- legacy
- architecture
- decoupling
trust_rating: 0.95
estimated_tokens: 1500
description: Systematically modernize legacy monoliths, eliminate god classes, extract
  micro-modules using the Strangler Fig pattern, and introduce characterization tests.
trigger_patterns:
- refactor legacy codebase
- modernize old code
- decouple monolithic class
- extract module from monolith
- strangler fig pattern
---

# Legacy Codebase Modernizer & Decoupling

## Objective
Safely refactor legacy, tightly-coupled code into modular, modern architecture without breaking existing production behavior.

## Systematic 4-Step Protocol
1. **Characterization Tests**: Write golden-master / snapshot tests capturing existing output before modifying any logic.
2. **Interface Extraction**: Wrap untyped dependencies in clear protocol / abstract interfaces.
3. **Strangler Fig Migration**: Route new requests through a facade; incrementally replace old execution branches.
4. **Dead Code Pruning**: Verify coverage and purge obsolete legacy pathways.
