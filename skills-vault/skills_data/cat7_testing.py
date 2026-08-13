"""
Category 7: Testing & QA Automation (4 Skills)
"""

TESTING_QA_SKILLS = [
    {
        "id": "testing-qa-automation.unit-integration-python.pytest-mocking-mastery",
        "name": "pytest-mocking-mastery",
        "title": "Pytest Fixture Architecture, Async Mocks & Parametrization",
        "category": "testing-qa-automation",
        "subcategory": "unit-integration-python",
        "version": "1.4.0",
        "tags": ["pytest", "unittest-mock", "python", "fixtures", "parametrize", "pytest-asyncio"],
        "trust_rating": 0.99,
        "estimated_tokens": 1650,
        "description": "Design modular, maintainable Pytest test suites with conftest fixtures, AsyncMock and MagicMock patching, parameterized test tables, and coverage enforcement.",
        "trigger_patterns": [
            "pytest fixtures conftest setup",
            "pytest async mock patching",
            "pytest mark parametrize table test",
            "pytest mock external api call"
        ],
        "content": """# Pytest Fixture Architecture, Async Mocks & Parametrization

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
"""
    },

    {
        "id": "testing-qa-automation.e2e-testing.playwright-e2e-automation",
        "name": "playwright-e2e-automation",
        "title": "Playwright E2E Automation, Page Object Model & Visual Regression",
        "category": "testing-qa-automation",
        "subcategory": "e2e-testing",
        "version": "1.3.0",
        "tags": ["playwright", "e2e-testing", "typescript", "page-object-model", "test-automation", "snapshots"],
        "trust_rating": 0.98,
        "estimated_tokens": 1600,
        "description": "Construct resilient end-to-end browser automation suites with Playwright using the Page Object Model (POM), accessible role-based locators, and auth storage state reuse.",
        "trigger_patterns": [
            "playwright e2e test page object model",
            "playwright storageState auth reuse",
            "playwright getByRole locators",
            "playwright visual regression screenshot test"
        ],
        "content": """# Playwright E2E Automation & Page Object Model

## Objective
Author fast, flake-free browser automation tests using Playwright's Page Object Model (POM), auto-waiting accessibility locators (`getByRole`), and network route mocking.

## Page Object Model Blueprint (`tests/pages/LoginPage.ts`)
```typescript
import { type Page, type Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByRole('textbox', { name: /email/i });
    this.passwordInput = page.getByRole('textbox', { name: /password/i });
    this.submitButton = page.getByRole('button', { name: /sign in/i });
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, pass: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(pass);
    await this.submitButton.click();
    await expect(this.page).toHaveURL('/dashboard');
  }
}
```

## Anti-Patterns
- ❌ Hardcoding arbitrary sleep delays (`page.waitForTimeout(5000)`). Use Playwright's built-in auto-waiting assertions (`await expect(locator).toBeVisible()`).
"""
    },

    {
        "id": "testing-qa-automation.frontend-unit.vitest-react-testing-library",
        "name": "vitest-react-testing-library",
        "title": "Vitest & React Testing Library (RTL) Component Testing",
        "category": "testing-qa-automation",
        "subcategory": "frontend-unit",
        "version": "1.3.0",
        "tags": ["vitest", "react-testing-library", "rtl", "user-event", "jsdom", "unit-testing"],
        "trust_rating": 0.97,
        "estimated_tokens": 1500,
        "description": "Author lightning-fast React component unit tests using Vitest, React Testing Library, user-event interactions, and accessibility-first queries.",
        "trigger_patterns": [
            "vitest react testing library setup",
            "test react component user-event",
            "rtl getByRole accessibility queries",
            "mock service worker msw vitest"
        ],
        "content": """# Vitest & React Testing Library Component Testing

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
"""
    },

    {
        "id": "testing-qa-automation.load-testing.locust-performance-load-testing",
        "name": "locust-performance-load-testing",
        "title": "Locust Distributed Load Testing & Latency Benchmarking",
        "category": "testing-qa-automation",
        "subcategory": "load-testing",
        "version": "1.2.0",
        "tags": ["locust", "load-testing", "performance", "benchmarking", "stress-testing", "python"],
        "trust_rating": 0.96,
        "estimated_tokens": 1500,
        "description": "Benchmark API throughput, p95/p99 latencies, and concurrency limits using Locust Python-as-code distributed load test scenarios.",
        "trigger_patterns": [
            "locust python load testing setup",
            "benchmark api p99 latency locust",
            "distributed load testing locust workers",
            "locust task weighting user journey"
        ],
        "content": """# Locust Distributed Load Testing & Latency Benchmarking

## Objective
Simulate thousands of concurrent user journeys in pure Python to uncover system concurrency ceilings, database connection pool exhaustion, and memory leaks.

## Load Scenario Blueprint (`locustfile.py`)
```python
from locust import HttpUser, task, between

class APIStressUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task(3)
    def view_catalog(self):
        self.client.get("/v1/items?limit=20", name="/v1/items")

    @task(1)
    def place_order(self):
        payload = {"sku": "SKU-999", "quantity": 1}
        with self.client.post("/v1/orders", json=payload, name="/v1/orders", catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Failed with status: {response.status_code}")
```

## Anti-Patterns
- ❌ Running high-concurrency load tests from a single machine without distributed worker nodes.
"""
    }
]
