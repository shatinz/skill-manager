---
id: testing-quality.unit-integration.playwright-e2e-automation
name: playwright-e2e-automation
title: Playwright End-to-End Test Automation & Flake Elimination
category: testing-quality
subcategory: unit-integration
version: 1.1.0
tags:
- playwright
- e2e
- testing
- typescript
- browser-automation
trust_rating: 0.94
estimated_tokens: 1400
description: Construct rock-solid Playwright end-to-end tests with Page Object Models,
  auto-waiting locators, network request mocking, and visual regression snapshots.
trigger_patterns:
- write playwright e2e tests
- playwright page object model
- fix flaky playwright test
- visual regression playwright
---

# Playwright End-to-End Test Automation

## Best Practices
- Never use `page.waitForTimeout()`. Rely on web-first assertions (`expect(locator).toBeVisible()`).
- Use accessible role-based locators: `page.getByRole('button', { name: 'Submit' })`.
- Save and reuse authenticated browser storage state (`storageState`) to avoid logging in for every test.
