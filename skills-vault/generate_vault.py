#!/usr/bin/env python3
"""
Public Agentic Skill Vault Generator & Index Compiler
Generates rich, production-grade SKILL.md documents organized by category and subcategory.
"""

import os
import json
import yaml
import re

VAULT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(VAULT_DIR, "skills")

SKILLS_DATA = [
    # 1. CODING -> API DESIGN
    {
        "id": "coding.api-design.fastapi-rest-craft",
        "name": "fastapi-rest-craft",
        "title": "FastAPI REST API Production Craft",
        "category": "coding",
        "subcategory": "api-design",
        "version": "1.2.0",
        "tags": ["fastapi", "python", "pydantic", "rest-api", "crud", "openapi"],
        "trust_rating": 0.96,
        "estimated_tokens": 1400,
        "description": "Architect, implement, and harden production-grade FastAPI REST services with Pydantic v2 schemas, async database sessions, dependency injection, and standardized RFC 7807 error envelopes.",
        "trigger_patterns": [
            "create a fastapi backend",
            "build rest api with fastapi",
            "fastapi crud endpoints",
            "pydantic v2 models for fastapi",
            "async sqlalchemy fastapi"
        ],
        "content": """# FastAPI REST API Production Craft

## Objective
Implement high-throughput, maintainable, and type-safe REST APIs using FastAPI and Pydantic v2 with clean layered architecture (Routers -> Services -> Repositories -> Models).

## Architectural Guidelines
1. **Layered Structure**: Keep route handlers lightweight. Delegate business logic to services and database queries to repositories.
2. **Schema Separation**: Never expose ORM models directly. Use `ItemCreate`, `ItemUpdate`, `ItemResponse`, and `ItemFilter` Pydantic schemas.
3. **Dependency Injection**: Use `Depends()` for database sessions, authentication context, rate limiters, and service singletons.
4. **Error Handling**: Use custom application exceptions mapped to standard HTTP status codes via global exception handlers.

## Standard Code Blueprint

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid

router = APIRouter(prefix="/v1/items", tags=["Items"])

# Schemas
class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: uuid.UUID
    created_at: str
    model_config = ConfigDict(from_attributes=True)

# Endpoints
@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(payload: ItemCreate, db: AsyncSession = Depends(get_db)):
    item = await item_service.create_item(db, payload)
    return item

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    item = await item_service.get_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

## Anti-Patterns & Verification
- ❌ Do NOT run blocking I/O (synchronous file reads, time.sleep) in `async def` routes.
- ❌ Do NOT return raw SQLAlchemy models directly without Pydantic serialization.
- ✅ Always write pytest-asyncio integration tests verifying status codes, schema validation, and headers.
"""
    },

    # 2. CODING -> API DESIGN
    {
        "id": "coding.api-design.graphql-schema-design",
        "name": "graphql-schema-design",
        "title": "GraphQL Schema Architecture & Federation",
        "category": "coding",
        "subcategory": "api-design",
        "version": "1.0.0",
        "tags": ["graphql", "strawberry", "apollo", "schema", "api", "python", "typescript"],
        "trust_rating": 0.91,
        "estimated_tokens": 1200,
        "description": "Design modular, scalable GraphQL schemas with type safety, DataLoader N+1 query batching, relay-style cursor pagination, and schema-first evolution.",
        "trigger_patterns": [
            "design graphql schema",
            "fix n+1 graphql dataloader",
            "strawberry graphql python",
            "graphql cursor pagination",
            "apollo federation schema"
        ],
        "content": """# GraphQL Schema Architecture & Federation

## Objective
Design robust GraphQL APIs that prevent N+1 query cascades, support Relay cursor pagination, and enforce strict type definitions.

## Key Principles
1. **DataLoader Optimization**: Every relational field resolver MUST use a batch DataLoader to collapse $N$ queries into a single batch query.
2. **Relay Cursor Connections**: Use `edges`, `node`, `pageInfo`, and opaque cursors for all collection fields.
3. **Mutation Responses**: Always return an object with a payload and user-facing error list, not bare booleans or raw entity types.

## Verification Checklist
- Run DataLoader benchmarks to confirm batching collapses queries.
- Verify introspection query performance and enforce query depth limiting.
"""
    },

    # 3. CODING -> API DESIGN
    {
        "id": "coding.api-design.grpc-protobuf-specs",
        "name": "grpc-protobuf-specs",
        "title": "gRPC & Protocol Buffers Microservice Specs",
        "category": "coding",
        "subcategory": "api-design",
        "version": "1.0.0",
        "tags": ["grpc", "protobuf", "microservices", "rpc", "go", "python"],
        "trust_rating": 0.89,
        "estimated_tokens": 1150,
        "description": "Define high-performance backward-compatible gRPC service definitions, Proto3 contracts, streaming RPCs, and status code propagation across distributed services.",
        "trigger_patterns": [
            "create grpc proto file",
            "protobuf backward compatibility",
            "grpc streaming rpc",
            "microservice proto definition"
        ],
        "content": """# gRPC & Protocol Buffers Microservice Specs

## Objective
Author clean, forward/backward compatible Proto3 service definitions with field reservation, well-known types, and streaming semantics.

## Best Practices
- Never reuse or reorder field tags. Use `reserved 4, 12 to 15;` when deleting fields.
- Wrap optional primitives in `google.protobuf.StringValue` or Proto3 `optional`.
- Use gRPC rich error model (`google.rpc.Status`) with `ErrorInfo` and `BadRequest` details.
"""
    },

    # 4. CODING -> DATABASE ARCHITECTURE
    {
        "id": "coding.database-architecture.postgres-query-tuning",
        "name": "postgres-query-tuning",
        "title": "PostgreSQL Performance Optimization & Query Tuning",
        "category": "coding",
        "subcategory": "database-architecture",
        "version": "1.3.0",
        "tags": ["postgres", "sql", "performance", "indexing", "explain-analyze", "database"],
        "trust_rating": 0.98,
        "estimated_tokens": 1600,
        "description": "Diagnose slow SQL queries, analyze EXPLAIN (ANALYZE, BUFFERS) plans, design composite/partial/BRIN indexes, and tune PostgreSQL memory parameters.",
        "trigger_patterns": [
            "optimize slow sql query",
            "postgres explain analyze",
            "design postgres indexes",
            "tune postgres database performance",
            "resolve sequential scan postgres"
        ],
        "content": """# PostgreSQL Performance Optimization & Query Tuning

## Objective
Transform high-latency SQL queries into microsecond execution plans using advanced indexing strategies, query rewriting, and buffer inspection.

## Execution Analysis Workflow
1. Run `EXPLAIN (ANALYZE, BUFFERS, SETTINGS) <query>;`
2. Check `Buffers: shared hit=... read=...`. High `read` indicates disk I/O bottlenecks.
3. Identify `Seq Scan` on large tables, `Hash Join` with excessive batch spillage, and expensive `Sort` operations.

## Indexing Decision Matrix
- **B-Tree**: Default equality, range (`<`, `<=`, `>=`, `>`), and `ORDER BY`.
- **Composite Index**: Put high-cardinality equality columns first, followed by range column: `CREATE INDEX ON orders (user_id, status, created_at DESC);`.
- **Partial Index**: For filtered hot sets: `CREATE INDEX ON tasks (priority) WHERE status = 'pending';`.
- **GIN**: For JSONB containment (`@>`), full-text search (`tsvector`), and array overlap (`&&`).
"""
    },

    # 5. CODING -> DATABASE ARCHITECTURE
    {
        "id": "coding.database-architecture.prisma-orm-patterns",
        "name": "prisma-orm-patterns",
        "title": "Prisma ORM Type-Safe Data Modeling & Migrations",
        "category": "coding",
        "subcategory": "database-architecture",
        "version": "1.1.0",
        "tags": ["prisma", "typescript", "orm", "database", "migrations", "nodejs"],
        "trust_rating": 0.92,
        "estimated_tokens": 1300,
        "description": "Master type-safe database access with Prisma ORM in TypeScript, including relation queries, interactive transactions, nested writes, and zero-downtime migrations.",
        "trigger_patterns": [
            "prisma schema design",
            "prisma interactive transactions",
            "prisma migrations typescript",
            "optimize prisma queries"
        ],
        "content": """# Prisma ORM Type-Safe Data Modeling & Migrations

## Objective
Model complex relational domains in `schema.prisma`, execute atomic interactive transactions, and prevent over-fetching using type-safe select payloads.

## Rules
- Use `$transaction(async (tx) => { ... })` for multi-step mutations.
- Prefer explicit `select` over unbounded `include` to minimize wire payload.
- Always run `prisma migrate dev` during local development and `prisma migrate deploy` in production CI/CD.
"""
    },

    # 6. CODING -> REFACTORING CLEAN CODE
    {
        "id": "coding.refactoring-clean-code.legacy-code-modernizer",
        "name": "legacy-code-modernizer",
        "title": "Legacy Codebase Modernizer & Decoupling",
        "category": "coding",
        "subcategory": "refactoring-clean-code",
        "version": "1.2.0",
        "tags": ["refactoring", "clean-code", "legacy", "architecture", "decoupling"],
        "trust_rating": 0.95,
        "estimated_tokens": 1500,
        "description": "Systematically modernize legacy monoliths, eliminate god classes, extract micro-modules using the Strangler Fig pattern, and introduce characterization tests.",
        "trigger_patterns": [
            "refactor legacy codebase",
            "modernize old code",
            "decouple monolithic class",
            "extract module from monolith",
            "strangler fig pattern"
        ],
        "content": """# Legacy Codebase Modernizer & Decoupling

## Objective
Safely refactor legacy, tightly-coupled code into modular, modern architecture without breaking existing production behavior.

## Systematic 4-Step Protocol
1. **Characterization Tests**: Write golden-master / snapshot tests capturing existing output before modifying any logic.
2. **Interface Extraction**: Wrap untyped dependencies in clear protocol / abstract interfaces.
3. **Strangler Fig Migration**: Route new requests through a facade; incrementally replace old execution branches.
4. **Dead Code Pruning**: Verify coverage and purge obsolete legacy pathways.
"""
    },

    # 7. CODING -> REFACTORING CLEAN CODE
    {
        "id": "coding.refactoring-clean-code.dry-solid-refactor",
        "name": "dry-solid-refactor",
        "title": "DRY & SOLID Architecture Refactoring",
        "category": "coding",
        "subcategory": "refactoring-clean-code",
        "version": "1.0.0",
        "tags": ["solid", "dry", "design-patterns", "clean-architecture", "refactoring"],
        "trust_rating": 0.93,
        "estimated_tokens": 1250,
        "description": "Apply Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion principles to eliminate code duplication and fragility.",
        "trigger_patterns": [
            "apply solid principles",
            "clean code refactoring",
            "dry refactor duplicate code",
            "dependency inversion refactor"
        ],
        "content": """# DRY & SOLID Architecture Refactoring

## Core Principles in Action
- **Single Responsibility (SRP)**: Each class/module must have only one reason to change.
- **Open/Closed (OCP)**: Extend behavior via strategy objects or plugins rather than modifying core conditional branches.
- **Dependency Inversion (DIP)**: Depend upon abstractions, not concrete implementations.
"""
    },

    # 8. CODING -> FRONTEND ENGINEERING
    {
        "id": "coding.frontend-engineering.react-performance-audit",
        "name": "react-performance-audit",
        "title": "React & Next.js Performance Audit & Optimization",
        "category": "coding",
        "subcategory": "frontend-engineering",
        "version": "1.2.0",
        "tags": ["react", "nextjs", "performance", "frontend", "web-vitals", "re-render"],
        "trust_rating": 0.97,
        "estimated_tokens": 1550,
        "description": "Eliminate wasted React re-renders, optimize Core Web Vitals (LCP, INP, CLS), implement smart memoization, virtualization for large lists, and dynamic code splitting.",
        "trigger_patterns": [
            "fix react re-renders",
            "optimize nextjs performance",
            "audit react performance",
            "improve core web vitals",
            "react memo usecallback audit"
        ],
        "content": """# React & Next.js Performance Audit & Optimization

## Objective
Diagnose and eliminate UI stutter, high Interaction to Next Paint (INP), and redundant component re-render cascades.

## Diagnostic Strategy
1. **React DevTools Profiler**: Record user interaction, filter by 'Why did this render?'.
2. **State Colocation**: Move ephemeral state down to leaf components to isolate re-render boundaries.
3. **List Virtualization**: Use TanStack Virtual for lists exceeding 100 items.
4. **Bundle Splitting**: Replace heavy static imports with `next/dynamic` or `React.lazy`.
"""
    },

    # 9. CODING -> FRONTEND ENGINEERING
    {
        "id": "coding.frontend-engineering.tailwind-design-system",
        "name": "tailwind-design-system",
        "title": "Tailwind CSS Tokenized Design System Architecture",
        "category": "coding",
        "subcategory": "frontend-engineering",
        "version": "1.0.0",
        "tags": ["tailwind", "css", "design-system", "tokens", "dark-mode", "ui"],
        "trust_rating": 0.94,
        "estimated_tokens": 1300,
        "description": "Build consistent, accessible, and themeable UI component systems with Tailwind CSS tokens, CSS variables, semantic color palettes, and glassmorphism.",
        "trigger_patterns": [
            "build tailwind design system",
            "tailwind css tokens dark mode",
            "create reusable tailwind components",
            "themeable tailwind system"
        ],
        "content": """# Tailwind CSS Tokenized Design System Architecture

## Objective
Establish a centralized design system using semantic CSS custom properties, HSL color tokens, and accessible component variants via `cva` (class-variance-authority).
"""
    },

    # 10. TESTING -> UNIT & INTEGRATION
    {
        "id": "testing-quality.unit-integration.pytest-mocking-mastery",
        "name": "pytest-mocking-mastery",
        "title": "Pytest Fixtures, Mocking & Async Test Suite",
        "category": "testing-quality",
        "subcategory": "unit-integration",
        "version": "1.4.0",
        "tags": ["pytest", "python", "testing", "mocking", "fixtures", "coverage"],
        "trust_rating": 0.99,
        "estimated_tokens": 1500,
        "description": "Author deterministic, blazing-fast pytest test suites using scoped fixtures, monkeypatching, respx HTTP mocking, factory-boy test data, and parametrize matrices.",
        "trigger_patterns": [
            "write pytest tests",
            "pytest async mocking",
            "pytest fixtures best practices",
            "mock external api pytest",
            "pytest parametrize test cases"
        ],
        "content": """# Pytest Fixtures, Mocking & Async Test Suite

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
"""
    },

    # 11. TESTING -> UNIT & INTEGRATION
    {
        "id": "testing-quality.unit-integration.playwright-e2e-automation",
        "name": "playwright-e2e-automation",
        "title": "Playwright End-to-End Test Automation & Flake Elimination",
        "category": "testing-quality",
        "subcategory": "unit-integration",
        "version": "1.1.0",
        "tags": ["playwright", "e2e", "testing", "typescript", "browser-automation"],
        "trust_rating": 0.94,
        "estimated_tokens": 1400,
        "description": "Construct rock-solid Playwright end-to-end tests with Page Object Models, auto-waiting locators, network request mocking, and visual regression snapshots.",
        "trigger_patterns": [
            "write playwright e2e tests",
            "playwright page object model",
            "fix flaky playwright test",
            "visual regression playwright"
        ],
        "content": """# Playwright End-to-End Test Automation

## Best Practices
- Never use `page.waitForTimeout()`. Rely on web-first assertions (`expect(locator).toBeVisible()`).
- Use accessible role-based locators: `page.getByRole('button', { name: 'Submit' })`.
- Save and reuse authenticated browser storage state (`storageState`) to avoid logging in for every test.
"""
    },

    # 12. TESTING -> SECURITY SAST
    {
        "id": "testing-quality.security-sast.owasp-top10-scanner",
        "name": "owasp-top10-scanner",
        "title": "OWASP Top 10 SAST Security Auditing & Remediation",
        "category": "testing-quality",
        "subcategory": "security-sast",
        "version": "1.3.0",
        "tags": ["security", "owasp", "sast", "vulnerability", "audit", "injection"],
        "trust_rating": 0.98,
        "estimated_tokens": 1600,
        "description": "Scan codebases for OWASP Top 10 vulnerabilities (SQLi, XSS, SSRF, IDOR, Broken Auth, Command Injection) and implement robust automated security controls.",
        "trigger_patterns": [
            "audit owasp vulnerabilities",
            "security audit code",
            "fix sql injection xss",
            "sast security scanning",
            "check for idor ssrf"
        ],
        "content": """# OWASP Top 10 SAST Security Auditing & Remediation

## Scan & Audit Rules
1. **Injection (A03)**: Ban string interpolation in SQL/OS queries. Enforce parameterized queries and ORMs.
2. **Broken Access Control (A01)**: Enforce tenant ID verification on every single object lookup (prevent IDOR).
3. **SSRF (A10)**: Validate and whitelist target hosts for server-side outbound webhooks/fetch. Disallow private IP subnets (`127.0.0.1`, `10.0.0.0/8`, `169.254.169.254`).
"""
    },

    # 13. TESTING -> SECURITY SAST
    {
        "id": "testing-quality.security-sast.secret-leak-detector",
        "name": "secret-leak-detector",
        "title": "Automated Secret Leak Detection & Git Pre-Commit Guard",
        "category": "testing-quality",
        "subcategory": "security-sast",
        "version": "1.0.0",
        "tags": ["secrets", "gitleaks", "git-guard", "security", "api-keys"],
        "trust_rating": 0.95,
        "estimated_tokens": 1100,
        "description": "Prevent accidental commits of API keys, private certificates, JWT secrets, and database credentials using regex entropy patterns and pre-commit hooks.",
        "trigger_patterns": [
            "detect leaked secrets",
            "scan for api keys in code",
            "gitleaks pre-commit setup",
            "prevent credential leak"
        ],
        "content": """# Automated Secret Leak Detection & Git Pre-Commit Guard

## Rules
- Match high-entropy strings and vendor prefix tokens (`sk_live_`, `ghp_`, `AKIA...`, `BEGIN RSA PRIVATE KEY`).
- Block commits with `pre-commit` and run Gitleaks in CI before merges.
"""
    },

    # 14. DEVOPS -> CI/CD
    {
        "id": "devops-cloud.ci-cd.github-actions-matrix-ci",
        "name": "github-actions-matrix-ci",
        "title": "GitHub Actions Multi-Matrix CI/CD Pipeline",
        "category": "devops-cloud",
        "subcategory": "ci-cd",
        "version": "1.2.0",
        "tags": ["github-actions", "ci-cd", "devops", "automation", "matrix", "caching"],
        "trust_rating": 0.96,
        "estimated_tokens": 1400,
        "description": "Construct high-speed, cached GitHub Actions workflows with test matrices (OS, Python/Node versions), security linting, Docker layer caching, and deployment gates.",
        "trigger_patterns": [
            "write github actions workflow",
            "github actions matrix build",
            "cache dependencies github actions",
            "ci cd pipeline github"
        ],
        "content": """# GitHub Actions Multi-Matrix CI/CD Pipeline

## Key Optimizations
- Use `actions/cache` for pip/npm/cargo dependencies.
- Enable `concurrency: group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true` to kill superseded commits.
- Use Docker Buildx with GitHub Actions cache backend (`type=gha`).
"""
    },

    # 15. DEVOPS -> CI/CD
    {
        "id": "devops-cloud.ci-cd.docker-multi-stage-build",
        "name": "docker-multi-stage-build",
        "title": "Production Docker Multi-Stage Optimization & Distroless",
        "category": "devops-cloud",
        "subcategory": "ci-cd",
        "version": "1.3.0",
        "tags": ["docker", "container", "multi-stage", "distroless", "security", "devops"],
        "trust_rating": 0.98,
        "estimated_tokens": 1350,
        "description": "Author minimal, secure, and reproducible Docker images using multi-stage builds, non-root users, unprivileged distroless base images, and `.dockerignore`.",
        "trigger_patterns": [
            "optimize dockerfile",
            "docker multi stage build",
            "distroless docker image",
            "secure docker container non-root"
        ],
        "content": """# Production Docker Multi-Stage Optimization & Distroless

```dockerfile
# Stage 1: Build dependencies
FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Final Minimal Runtime
FROM gcr.io/distroless/python3-debian12:nonroot
WORKDIR /app
COPY --from=builder /app/wheels /wheels
RUN ["/usr/bin/pip", "install", "--no-index", "--find-links=/wheels", "-r", "requirements.txt"]
COPY --chown=nonroot:nonroot . .
USER nonroot
ENTRYPOINT ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
"""
    },

    # 16. DEVOPS -> INFRASTRUCTURE AS CODE
    {
        "id": "devops-cloud.infrastructure-as-code.terraform-aws-modules",
        "name": "terraform-aws-modules",
        "title": "Terraform AWS Modular Architecture & State Management",
        "category": "devops-cloud",
        "subcategory": "infrastructure-as-code",
        "version": "1.1.0",
        "tags": ["terraform", "aws", "iac", "cloud", "s3", "state-locking"],
        "trust_rating": 0.93,
        "estimated_tokens": 1450,
        "description": "Design reusable, secure Terraform modules for AWS (VPC, ECS, RDS, IAM, S3) with remote S3 backend state locking and zero-hardcoded secrets.",
        "trigger_patterns": [
            "write terraform module aws",
            "terraform remote state s3",
            "iac aws infrastructure terraform",
            "terraform best practices"
        ],
        "content": """# Terraform AWS Modular Architecture

## Core Guidelines
- Store state in encrypted S3 bucket with DynamoDB table for state locking.
- Maintain separate environments (`dev`, `staging`, `prod`) using Terragrunt or distinct workspace state prefixes.
- Follow least privilege for IAM role definitions.
"""
    },

    # 17. DEVOPS -> OBSERVABILITY
    {
        "id": "devops-cloud.observability.prometheus-grafana-telemetry",
        "name": "prometheus-grafana-telemetry",
        "title": "Prometheus, Grafana & OpenTelemetry Observability Stack",
        "category": "devops-cloud",
        "subcategory": "observability",
        "version": "1.0.0",
        "tags": ["prometheus", "grafana", "opentelemetry", "metrics", "tracing", "monitoring"],
        "trust_rating": 0.91,
        "estimated_tokens": 1300,
        "description": "Instrument applications with OpenTelemetry traces, export RED metrics (Rate, Errors, Duration) to Prometheus, and design actionable Grafana alert dashboards.",
        "trigger_patterns": [
            "setup prometheus metrics",
            "grafana dashboard alerts",
            "opentelemetry tracing instrumentation",
            "red metrics monitoring"
        ],
        "content": """# Prometheus, Grafana & OpenTelemetry Observability Stack

## Metrics Checklist
- **Counter**: Total requests, failed jobs.
- **Histogram**: Latency distributions with exponential bucket sizing.
- **Gauge**: Active database connections, queue depths.
"""
    },

    # 18. DATA & AI -> LLM & RAG
    {
        "id": "data-ai-engineering.llm-rag.rag-chunking-hybrid-search",
        "name": "rag-chunking-hybrid-search",
        "title": "RAG Chunking, Hybrid Vector-BM25 Search & Reranking",
        "category": "data-ai-engineering",
        "subcategory": "llm-rag",
        "version": "1.3.0",
        "tags": ["rag", "llm", "embeddings", "bm25", "hybrid-search", "reranker", "vector-db"],
        "trust_rating": 0.98,
        "estimated_tokens": 1650,
        "description": "Build high-accuracy Retrieval-Augmented Generation (RAG) pipelines using semantic chunking, Reciprocal Rank Fusion (RRF) hybrid search, cross-encoder rerankers, and context compression.",
        "trigger_patterns": [
            "build rag pipeline",
            "hybrid search vector bm25",
            "semantic chunking rag",
            "cross-encoder reranking",
            "optimize rag accuracy"
        ],
        "content": """# RAG Chunking, Hybrid Vector-BM25 Search & Reranking

## Complete RAG Architecture Flow
1. **Semantic Chunking**: Split by document headings, paragraph boundaries, or embedding distance spikes rather than naive token counts.
2. **Dense Vector Search**: Compute embedding cosine similarity for semantic concepts.
3. **Sparse Lexical Search**: Run BM25 for exact keyword matches, code tokens, and acronyms.
4. **Reciprocal Rank Fusion (RRF)**:
   $$\text{RRF Score}(d) = \sum_{m \in \{dense, sparse\}} \frac{1}{60 + \text{rank}_m(d)}$$
5. **Cross-Encoder Reranker**: Pass top 25 RRF candidates through BGE-Reranker or Cohere Rerank to pick top 5.
"""
    },

    # 19. DATA & AI -> LLM & RAG
    {
        "id": "data-ai-engineering.llm-rag.prompt-engineering-distiller",
        "name": "prompt-engineering-distiller",
        "title": "System Prompt Engineering & Chain-of-Thought Distiller",
        "category": "data-ai-engineering",
        "subcategory": "llm-rag",
        "version": "1.2.0",
        "tags": ["prompt-engineering", "cot", "llm", "system-prompts", "evals"],
        "trust_rating": 0.95,
        "estimated_tokens": 1400,
        "description": "Engineer high-leverage agent system prompts with strict XML/JSON formatting, few-shot grounding examples, step-by-step reasoning triggers, and anti-hallucination guardrails.",
        "trigger_patterns": [
            "write system prompt for agent",
            "prompt engineering best practices",
            "chain of thought prompt template",
            "reduce llm hallucinations"
        ],
        "content": """# System Prompt Engineering & Chain-of-Thought Distiller

## Anatomy of an Unbeatable Agent Prompt
- **Identity & Mission**: Concrete role, purpose, and operating boundaries.
- **Explicit Constraints**: Negative constraints, disallowed assumptions, output constraints.
- **Input Formatting**: Clean XML tags (`<user_request>`, `<context>`, `<tools>`).
- **Chain of Thought**: Mandate hidden `<thinking>` scratchpad before producing final answer.
"""
    },

    # 20. DATA & AI -> DATA PIPELINES
    {
        "id": "data-ai-engineering.data-pipelines.duckdb-fast-analytics",
        "name": "duckdb-fast-analytics",
        "title": "DuckDB & Polars High-Speed In-Process Data Pipelines",
        "category": "data-ai-engineering",
        "subcategory": "data-pipelines",
        "version": "1.1.0",
        "tags": ["duckdb", "polars", "python", "analytics", "parquet", "sql"],
        "trust_rating": 0.94,
        "estimated_tokens": 1300,
        "description": "Process gigabytes of Parquet, CSV, and JSON data in seconds using DuckDB's vectorized SQL engine and Polars lazy dataframes without external database clusters.",
        "trigger_patterns": [
            "duckdb fast analytics python",
            "polars lazy dataframe pipeline",
            "process large parquet files",
            "fast in-memory data processing"
        ],
        "content": """# DuckDB & Polars High-Speed In-Process Data Pipelines

## Highlights
- Query directly from remote S3/HTTP Parquet files with zero ingestion overhead.
- Stream larger-than-RAM datasets using DuckDB out-of-core execution.
"""
    },

    # 21. SECURITY -> CODE HARDENING
    {
        "id": "security-compliance.code-hardening.jwt-oauth2-secureshop",
        "name": "jwt-oauth2-secureshop",
        "title": "OAuth2 & JWT Token Security Architecture",
        "category": "security-compliance",
        "subcategory": "code-hardening",
        "version": "1.2.0",
        "tags": ["oauth2", "jwt", "auth", "security", "tokens", "fastapi", "nodejs"],
        "trust_rating": 0.97,
        "estimated_tokens": 1450,
        "description": "Implement bulletproof JWT authentication and OAuth2 token lifecycles with asymmetric RS256/EdDSA signing, token revocation blacklists, and rotation.",
        "trigger_patterns": [
            "implement secure jwt auth",
            "oauth2 token rotation",
            "jwt rs256 asymmetric signing",
            "refresh token revocation"
        ],
        "content": """# OAuth2 & JWT Token Security Architecture

## Security Invariants
1. **Algorithm Whitelist**: Strictly enforce `algorithm="RS256"` or `"EdDSA"`. Never trust header `alg: none`.
2. **Short-Lived Access Tokens**: 5 to 15 minutes validity max.
3. **Opaque Refresh Tokens**: Store hashed in Redis with single-use rotation detection.
"""
    },

    # 22. SECURITY -> CODE HARDENING
    {
        "id": "security-compliance.code-hardening.input-sanitization-guard",
        "name": "input-sanitization-guard",
        "title": "Input Sanitization, Schema Validation & XSS Defense",
        "category": "security-compliance",
        "subcategory": "code-hardening",
        "version": "1.0.0",
        "tags": ["sanitization", "xss", "security", "validation", "pydantic", "zod"],
        "trust_rating": 0.93,
        "estimated_tokens": 1200,
        "description": "Defend against DOM XSS, prototype pollution, HTML injection, and untrusted payload deserialization using strict schema boundaries (Zod/Pydantic) and DOMPurify.",
        "trigger_patterns": [
            "input sanitization security",
            "prevent xss attacks",
            "validate untrusted input",
            "dompurify sanitize html"
        ],
        "content": """# Input Sanitization, Schema Validation & XSS Defense

## Validation Directives
- Parse and strip all untrusted HTML through DOMPurify with strict allowed tags.
- Reject unknown object keys in API payloads (`extra='forbid'`).
"""
    },

    # 23. DOCUMENTATION -> API DOCS
    {
        "id": "documentation-communication.api-docs.openapi-swagger-generator",
        "name": "openapi-swagger-generator",
        "title": "OpenAPI 3.1 & Swagger Documentation Architect",
        "category": "documentation-communication",
        "subcategory": "api-docs",
        "version": "1.1.0",
        "tags": ["openapi", "swagger", "documentation", "api-docs", "rest"],
        "trust_rating": 0.92,
        "estimated_tokens": 1250,
        "description": "Generate comprehensive, interactive OpenAPI 3.1 specifications with clear endpoint summaries, JSON request/response examples, status codes, and authentication schemas.",
        "trigger_patterns": [
            "generate openapi specification",
            "document rest api swagger",
            "openapi 3.1 schema examples",
            "api documentation standards"
        ],
        "content": """# OpenAPI 3.1 & Swagger Documentation Architect

## Documentation Standard
- Every endpoint MUST document `200/201`, `400`, `401/403`, `404`, and `500` response structures.
- Include realistic request and response example payloads for every route.
"""
    },

    # 24. DOCUMENTATION -> ADR
    {
        "id": "documentation-communication.architecture-decision-records.adr-writer-reviewer",
        "name": "adr-writer-reviewer",
        "title": "Architecture Decision Record (ADR) Writer & Reviewer",
        "category": "documentation-communication",
        "subcategory": "architecture-decision-records",
        "version": "1.0.0",
        "tags": ["adr", "architecture", "decisions", "documentation", "rfc"],
        "trust_rating": 0.94,
        "estimated_tokens": 1150,
        "description": "Document significant technical architecture decisions using standard ADR templates (Context, Decision, Consequences, Status, Alternatives Considered).",
        "trigger_patterns": [
            "write architecture decision record",
            "adr template for system design",
            "document technical decision",
            "software architecture rfc"
        ],
        "content": """# Architecture Decision Record (ADR) Writer & Reviewer

## Standard ADR Structure
- **Title**: `ADR-00X: <Short Decision Summary>`
- **Status**: Proposed / Accepted / Deprecated / Superseded
- **Context**: What problem are we solving? What are the business and technical constraints?
- **Decision**: What is the chosen solution and technical blueprint?
- **Consequences**: What becomes easier? What trade-offs or technical debt do we accept?
- **Alternatives Considered**: What options were evaluated and why were they rejected?
"""
    }
]

def generate_vault():
    print(f"[*] Generating {len(SKILLS_DATA)} production skills into {SKILLS_DIR}...")
    
    categories_tree = {}
    vault_index = {
        "version": "1.0.0",
        "vault_name": "Public Agentic Skill Vault",
        "total_skills": len(SKILLS_DATA),
        "categories": {},
        "skills": []
    }

    for item in SKILLS_DATA:
        cat = item["category"]
        subcat = item["subcategory"]
        skill_name = item["name"]
        
        target_dir = os.path.join(SKILLS_DIR, cat, subcat, skill_name)
        os.makedirs(target_dir, exist_ok=True)
        
        skill_file = os.path.join(target_dir, "SKILL.md")
        
        # Frontmatter
        frontmatter = {
            "id": item["id"],
            "name": item["name"],
            "title": item["title"],
            "category": item["category"],
            "subcategory": item["subcategory"],
            "version": item["version"],
            "tags": item["tags"],
            "trust_rating": item["trust_rating"],
            "estimated_tokens": item["estimated_tokens"],
            "description": item["description"],
            "trigger_patterns": item["trigger_patterns"]
        }
        
        yaml_header = yaml.dump(frontmatter, sort_keys=False).strip()
        full_document = f"---\n{yaml_header}\n---\n\n{item['content'].strip()}\n"
        
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(full_document)
            
        # Index entry (compact metadata)
        index_entry = {
            "id": item["id"],
            "name": item["name"],
            "title": item["title"],
            "category": item["category"],
            "subcategory": item["subcategory"],
            "version": item["version"],
            "tags": item["tags"],
            "trust_rating": item["trust_rating"],
            "estimated_tokens": item["estimated_tokens"],
            "description": item["description"],
            "trigger_patterns": item["trigger_patterns"],
            "relative_path": f"skills/{cat}/{subcat}/{skill_name}/SKILL.md"
        }
        vault_index["skills"].append(index_entry)
        
        # Update categories tree
        if cat not in categories_tree:
            categories_tree[cat] = {}
        if subcat not in categories_tree[cat]:
            categories_tree[cat][subcat] = []
        categories_tree[cat][subcat].append(item["name"])

    vault_index["categories"] = categories_tree

    # Write vault.json index
    index_path = os.path.join(VAULT_DIR, "vault.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(vault_index, f, indent=2)

    # Generate Vault README.md
    readme_path = os.path.join(VAULT_DIR, "README.md")
    readme_content = f"""# 🏛️ Public Agentic Skill Vault

> A community-driven, living ecosystem of reusable agentic capabilities, instructions, and workflows for autonomous AI agents.

## 📊 Overview
- **Total Skills**: {len(SKILLS_DATA)}
- **Categories**: {len(categories_tree)}
- **Subcategories**: {sum(len(v) for v in categories_tree.values())}

## 🗂️ Categories & Taxonomy

"""
    for cat, subcats in sorted(categories_tree.items()):
        readme_content += f"### 📁 `{cat}`\n"
        for subcat, skill_list in sorted(subcats.items()):
            readme_content += f"- **`{subcat}`** ({len(skill_list)} skills)\n"
            for sk in skill_list:
                readme_content += f"  - [`{sk}`](skills/{cat}/{subcat}/{sk}/SKILL.md)\n"
        readme_content += "\n"

    readme_content += """## ⚡ Using with the `askill` CLI

Agents can discover and fetch skills on-demand without cloning the entire repository:

```bash
# Smart search by task intent
askill search "build production rest api with postgres"

# Inject matching skill directly into agent prompt
askill match --task "optimize react re-renders"

# Fetch skill markdown on demand
askill get coding.api-design.fastapi-rest-craft

# Propose an improvement or PR
askill propose --skill coding.api-design.fastapi-rest-craft --file patch.diff --reason "Added Pydantic v2 model_config"
```

## 🤝 Contributing
Every skill is a living document. Propose updates via PR or submit proposals through the `askill propose` CLI.
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"[+] Successfully generated {len(SKILLS_DATA)} skills, vault.json, and README.md in {VAULT_DIR}!")

if __name__ == "__main__":
    generate_vault()
