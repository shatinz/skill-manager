---
id: testing-qa-automation.e2e-testing.playwright-e2e-automation
name: playwright-e2e-automation
title: Playwright E2E Automation, Page Object Model & Visual Regression
category: testing-qa-automation
subcategory: e2e-testing
version: 1.3.0
tags:
- playwright
- e2e-testing
- typescript
- page-object-model
- test-automation
- snapshots
trust_rating: 0.98
estimated_tokens: 1600
description: Construct resilient end-to-end browser automation suites with Playwright
  using the Page Object Model (POM), accessible role-based locators, and auth storage
  state reuse.
trigger_patterns:
- playwright e2e test page object model
- playwright storageState auth reuse
- playwright getByRole locators
- playwright visual regression screenshot test
---

# Playwright E2E Automation & Page Object Model

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
