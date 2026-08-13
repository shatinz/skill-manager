---
id: testing-qa-automation.unit-integration-python.pytest-mocking-mastery
name: pytest-mocking-mastery
title: Pytest Fixture Architecture, Async Mocks & Parametrization
category: testing-qa-automation
subcategory: unit-integration-python
version: 1.4.0
tags:
- pytest
- unittest-mock
- python
- fixtures
- parametrize
- pytest-asyncio
trust_rating: 0.99
estimated_tokens: 1650
description: Design modular, maintainable Pytest test suites with conftest fixtures,
  AsyncMock and MagicMock patching, parameterized test tables, and coverage enforcement.
trigger_patterns:
- pytest fixtures conftest setup
- pytest async mock patching
- pytest mark parametrize table test
- pytest mock external api call
---

# Pytest Fixture Architecture, Async Mocks & Parametrization

## Objective
Author fast, reliable, and decoupled unit/integration test suites in Python using Pytest fixture scopes, `unittest.mock.AsyncMock`, and parameterized test tables.

## Production Test Suite (`tests/test_payment_service.py`)
```python
import pytest
from unittest.mock import AsyncMock, patch
from dataclasses import dataclass

@dataclass
class PaymentResult:
    transaction_id: str
    success: bool

@pytest.fixture
def mock_payment_gateway():
    with patch("app.services.gateway.StripeGateway.charge", new_callable=AsyncMock) as mock_charge:
        mock_charge.return_value = PaymentResult(transaction_id="tx_123", success=True)
        yield mock_charge

@pytest.mark.parametrize("amount,currency,expected_fee", [
    (100.0, "USD", 3.20),
    (50.0, "USD", 1.75),
    (200.0, "EUR", 6.10),
])
@pytest.mark.asyncio
async def test_calculate_fee_and_charge(mock_payment_gateway, amount, currency, expected_fee):
    from app.services.billing import BillingService

    service = BillingService()
    res = await service.process_charge(amount=amount, currency=currency)

    assert res.success is True
    assert res.transaction_id == "tx_123"
    mock_payment_gateway.assert_awaited_once_with(amount=amount, currency=currency)
```

## Anti-Patterns
- ❌ Testing implementation details rather than public interface contracts.
- ❌ Using shared mutable global state in fixtures across test cases.
