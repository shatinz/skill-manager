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

## Strangler Fig Proxy Pattern Blueprint
```python
from typing import Callable, Any
import logging

logger = logging.getLogger("modernizer")

class StranglerProxy:
    def __init__(self, legacy_fn: Callable, modern_fn: Callable, rollout_percentage: float = 0.0):
        self.legacy_fn = legacy_fn
        self.modern_fn = modern_fn
        self.rollout_percentage = rollout_percentage

    async def execute(self, *args, **kwargs) -> Any:
        import random
        # Shadow mode: Execute both and compare in background
        if self.rollout_percentage <= 0:
            legacy_res = await self.legacy_fn(*args, **kwargs)
            try:
                modern_res = await self.modern_fn(*args, **kwargs)
                if legacy_res != modern_res:
                    logger.warning(f"Shadow mismatch! Legacy: {legacy_res} != Modern: {modern_res}")
            except Exception as e:
                logger.error(f"Modern shadow execution failed: {e}")
            return legacy_res
        
        # Progressive rollout
        if random.random() < self.rollout_percentage:
            return await self.modern_fn(*args, **kwargs)
        return await self.legacy_fn(*args, **kwargs)
```

## Anti-Patterns
- ❌ Attempting full 'Big-Bang' rewrites that halt business delivery for months and fail in production cutovers.
- ❌ Refactoring complex legacy logic without golden master characterization tests.
- ❌ Changing observable external behavior while refactoring internal code structure.

## Quality & Verification Checklist
- [ ] Golden master test suite passes against legacy code before refactoring begins.
- [ ] Strangler proxy routes live traffic with zero dropped requests or data inconsistency.
- [ ] Rollout percentage is configurable via environment variables or feature flags.
