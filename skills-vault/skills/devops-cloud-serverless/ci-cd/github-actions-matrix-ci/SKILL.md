---
id: devops-cloud-serverless.ci-cd.github-actions-matrix-ci
name: github-actions-matrix-ci
title: GitHub Actions Matrix CI/CD Workflows & Dependency Caching
category: devops-cloud-serverless
subcategory: ci-cd
version: 1.3.0
tags:
- github-actions
- ci-cd
- matrix-builds
- caching
- devops
- automation
trust_rating: 0.98
estimated_tokens: 1550
description: Construct high-speed, parallel matrix CI/CD workflows in GitHub Actions
  with deterministic dependency caching, concurrency controls, and OIDC cloud authentication.
trigger_patterns:
- github actions matrix build workflow
- github actions cache node_modules pip
- github actions concurrency cancel in progress
- github actions oidc aws deploy
---

# GitHub Actions Matrix CI/CD Workflows & Dependency Caching

## Objective
Accelerate continuous integration pipelines using parallel OS/version matrix builds, aggressive cache strategies, and secure OIDC deployments without long-lived access tokens.

## Production CI Workflow (`.github/workflows/ci.yml`)
```yaml
name: Continuous Integration

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test-matrix:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest]
        python-version: ['3.11', '3.12']
        node-version: ['20', '22']

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Setup Node ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          npm ci

      - name: Run Test Suite
        run: |
          pytest --cov=app --cov-report=xml
          npm test
```

## Anti-Patterns
- ❌ Missing concurrency cancellation, wasting runner minutes on stale PR commits.
- ❌ Hardcoding plain AWS credentials in GitHub Secrets instead of utilizing OIDC role assumption.
