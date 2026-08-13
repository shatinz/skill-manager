---
id: testing-quality.unit-integration.pytest-mocking-mastery
name: pytest-mocking-mastery
title: Pytest Fixtures, Mocking & Async Test Suite
category: testing-quality
subcategory: unit-integration
version: 1.4.0
tags:
- pytest
- python
- testing
- mocking
- fixtures
- coverage
trust_rating: 0.99
estimated_tokens: 1500
description: Author deterministic, blazing-fast pytest test suites using scoped fixtures,
  monkeypatching, respx HTTP mocking, factory-boy test data, and parametrize matrices.
trigger_patterns:
- write pytest tests
- pytest async mocking
- pytest fixtures best practices
- mock external api pytest
- pytest parametrize test cases
---

# Pytest Fixtures, Mocking & Async Test Suite

## Objective
Write maintainable, parallelizable unit and integration tests with zero flaky behavior.

## Key Techniques
1. **Scoped Fixtures**: Use `scope="session"` for expensive immutable containers and `scope="function"` for database rollbacks.
2. **Network Isolation**: Use `respx` or `aioresponses` to block and mock all outgoing HTTP traffic.
3. **Parametrization**: Test edge cases (empty strings, unicode, max bounds, nulls) with `@pytest.mark.parametrize`.

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_order_creation_success(mock_payment_gateway, test_db_session):
    mock_payment_gateway.charge.return_value = {"status": "succeeded", "tx_id": "tx_123"}
    service = OrderService(db=test_db_session, payment=mock_payment_gateway)
    
    order = await service.create_order(user_id="usr_1", amount=150.0)
    assert order.status == "PAID"
    mock_payment_gateway.charge.assert_awaited_once_with(amount=150.0)
```
