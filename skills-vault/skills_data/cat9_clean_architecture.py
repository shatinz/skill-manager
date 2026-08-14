"""
Category 9: Clean Architecture & Refactoring (4 Skills)
"""

CLEAN_ARCHITECTURE_SKILLS = [
    {
        "id": "clean-architecture-refactoring.principles-patterns.dry-solid-clean-architecture",
        "name": "dry-solid-clean-architecture",
        "title": "DRY, SOLID Principles & Clean Hexagonal Architecture",
        "category": "clean-architecture-refactoring",
        "subcategory": "principles-patterns",
        "version": "1.4.0",
        "tags": ["solid", "dry", "clean-architecture", "hexagonal-architecture", "domain-driven-design", "refactoring"],
        "trust_rating": 0.99,
        "estimated_tokens": 1700,
        "description": "Refactor monolithic and tightly-coupled codebases into Clean Hexagonal Architecture adhering to SOLID and DRY principles with decoupled domain entities, ports, and adapters.",
        "trigger_patterns": [
            "clean architecture refactoring solid",
            "hexagonal architecture ports and adapters",
            "dependency inversion python typescript",
            "dry solid principles code review"
        ],
        "content": """# DRY, SOLID Principles & Clean Hexagonal Architecture

## Objective
Decouple core business logic from framework and database dependencies by enforcing SOLID principles, Domain-Driven Design (DDD) boundaries, and Ports & Adapters (Hexagonal) architecture.

## Architectural Layers
1. **Domain Entities**: Pure enterprise business rules and immutable values. Zero external dependencies.
2. **Ports (Interfaces)**: Abstract contracts defining input/output operations (e.g., `UserRepositoryPort`, `NotificationPort`).
3. **Use Cases / Application Services**: Orchestrates domain entities to execute user goals.
4. **Adapters (Infrastructure)**: Concrete implementations of ports (e.g., `PostgresUserRepository`, `SendGridNotificationAdapter`).

## Hexagonal Blueprint in Python
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

# 1. Domain Entity (Pure Enterprise Logic)
@dataclass(frozen=True)
class User:
    id: str
    email: str
    is_active: bool

# 2. Port (Interface Contract)
class UserRepositoryPort(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def save(self, user: User) -> None:
        pass

# 3. Use Case (Application Orchestrator)
class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepositoryPort):
        self.user_repo = user_repo

    async def execute(self, email: str) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("Email already in use.")
        
        new_user = User(id="usr_123", email=email, is_active=True)
        await self.user_repo.save(new_user)
        return new_user
```

## Anti-Patterns
- ❌ Leaking database ORM models or HTTP request objects directly into domain entities.
- ❌ Premature DRY: Coupling two distinct domain contexts just because they currently share similar data fields.
- ❌ God Classes / Fat Services: Violating the Single Responsibility Principle by bundling auth, billing, and email in one class.

## Quality & Verification Checklist
- [ ] Domain models contain 0 imports from third-party ORMs or web frameworks.
- [ ] Ports use Python `abc.ABC` or TypeScript `interface` types.
- [ ] Use cases are 100% unit-testable using in-memory mock adapters without spinning up databases.
"""
    },

    {
        "id": "clean-architecture-refactoring.code-modernization.legacy-code-modernizer",
        "name": "legacy-code-modernizer",
        "title": "Legacy Code Modernization, Characterization Tests & Strangler Pattern",
        "category": "clean-architecture-refactoring",
        "subcategory": "code-modernization",
        "version": "1.3.0",
        "tags": ["refactoring", "legacy-code", "strangler-pattern", "characterization-tests", "technical-debt"],
        "trust_rating": 0.98,
        "estimated_tokens": 1600,
        "description": "Modernize legacy systems safely using the Strangler Fig pattern, characterization testing, incremental seams, and automated type enrichment.",
        "trigger_patterns": [
            "refactor legacy codebase strangler pattern",
            "characterization tests legacy code",
            "incremental modernization technical debt",
            "safely rewrite legacy monolith"
        ],
        "content": """# Legacy Code Modernization & Strangler Fig Pattern

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
"""
    },

    {
        "id": "clean-architecture-refactoring.architecture-patterns.event-driven-cqrs-messaging",
        "name": "event-driven-cqrs-messaging",
        "title": "Command Query Responsibility Segregation (CQRS) & Event-Driven Messaging",
        "category": "clean-architecture-refactoring",
        "subcategory": "architecture-patterns",
        "version": "1.3.0",
        "tags": ["cqrs", "event-driven", "message-bus", "event-sourcing", "outbox-pattern", "rabbitmq", "kafka"],
        "trust_rating": 0.97,
        "estimated_tokens": 1650,
        "description": "Architect scalable event-driven systems decoupling read and write models via CQRS, Transactional Outbox pattern, and idempotent event consumer handlers.",
        "trigger_patterns": [
            "cqrs event driven architecture",
            "transactional outbox pattern postgres",
            "idempotent event consumer message bus",
            "event sourcing command query separation"
        ],
        "content": """# Command Query Responsibility Segregation (CQRS) & Event-Driven Messaging

## Objective
Separate read and write data models (CQRS) and ensure guaranteed at-least-once event publication without dual-write inconsistency using the Transactional Outbox pattern.

## Transactional Outbox Pattern Blueprint
```sql
-- Outbox Table inside same ACID transaction as business mutation
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type VARCHAR(64) NOT NULL,
    aggregate_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(128) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ NULL
);
```

```python
async def place_order_with_outbox(session: AsyncSession, order_data: dict):
    async with session.begin():
        # 1. Mutate write database table
        order = Order(**order_data)
        session.add(order)
        await session.flush()

        # 2. Insert outbox record in the SAME atomic transaction
        outbox_event = OutboxEvent(
            aggregate_type="Order",
            aggregate_id=str(order.id),
            event_type="OrderPlaced",
            payload={"order_id": str(order.id), "total": order.total}
        )
        session.add(outbox_event)
```

## Anti-Patterns
- ❌ Committing to the database and publishing to Kafka/RabbitMQ in separate uncoordinated blocks (causes lost events on crash).
- ❌ Non-idempotent event consumers that fail or duplicate actions upon retried messages.

## Quality & Verification Checklist
- [ ] Write operations and outbox records execute in a single ACID transaction.
- [ ] Consumer handlers track processed message IDs in a deduplication table or Redis TTL key.
"""
    },

    {
        "id": "clean-architecture-refactoring.architectural-docs.adr-architecture-decision-records",
        "name": "adr-architecture-decision-records",
        "title": "Architecture Decision Records (ADR) Craft & Review",
        "category": "clean-architecture-refactoring",
        "subcategory": "architectural-docs",
        "version": "1.3.0",
        "tags": ["adr", "architecture", "decision-records", "documentation", "rfc", "governance"],
        "trust_rating": 0.99,
        "estimated_tokens": 1400,
        "description": "Document, evaluate, and track critical architectural trade-offs using structured Michael Nygard Architecture Decision Record (ADR) templates and decision matrices.",
        "trigger_patterns": [
            "write architecture decision record adr",
            "adr template michael nygard",
            "document technical trade offs adr",
            "architecture decision log governance"
        ],
        "content": """# Architecture Decision Records (ADR) Craft & Review

## Objective
Preserve long-term institutional knowledge and clarify architectural trade-offs by authoring structured, versioned Architecture Decision Records (ADRs).

## Standard Michael Nygard ADR Template (`docs/adr/0001-adopt-fastapi-and-postgres.md`)
```markdown
# 1. Adopt FastAPI & PostgreSQL for Core Microservice

Date: 2025-02-15
Status: Accepted

## Context
The legacy service struggles with synchronous blocking I/O and lacks type safety, leading to runtime data validation bugs under high concurrency.

## Decision
We will rewrite the core ingestion service in Python 3.12 using FastAPI, Pydantic v2, and SQLAlchemy 2.0 with PostgreSQL.

## Consequences
### Positive
- Native async I/O handles 5,000+ concurrent requests per second.
- Automatic OpenAPI documentation and strict Pydantic runtime schema validation.

### Negative / Trade-offs
- Engineers must adhere strictly to async database sessions and avoid blocking libraries.
```

## Anti-Patterns
- ❌ Authoring ADRs post-hoc without documenting rejected alternatives and negative consequences.
- ❌ Treating ADRs as immutable dogma rather than superseding them with new ADRs when requirements evolve.

## Quality & Verification Checklist
- [ ] Every ADR file follows numbered naming: `docs/adr/NNNN-title.md`.
- [ ] Status is clearly labeled: Proposed, Accepted, Deprecated, or Superseded by NNNN.
"""
    },

    {
        "id": "clean-architecture-refactoring.systems-engineering.rust-axum-tokio-async",
        "name": "rust-axum-tokio-async",
        "title": "Rust Axum & Tokio High-Throughput Async Architecture",
        "category": "clean-architecture-refactoring",
        "subcategory": "systems-engineering",
        "version": "1.3.0",
        "tags": ["rust", "axum", "tokio", "async", "sqlx", "tower", "high-performance", "zero-cost-abstractions"],
        "trust_rating": 0.99,
        "estimated_tokens": 1900,
        "description": "Architect ultra-high-throughput, memory-safe asynchronous web services and microservices using Rust, Axum, Tokio multi-threaded runtime, Tower middleware, and SQLx compile-time query validation.",
        "trigger_patterns": [
            "rust axum rest api server",
            "tokio async rust web service",
            "sqlx compile time postgres rust",
            "tower middleware layers axum"
        ],
        "content": """# Rust Axum & Tokio High-Throughput Async Architecture

## Objective
Engineer mission-critical, sub-millisecond latency backend microservices in Rust leveraging Axum's type-safe routing, Tokio multi-threaded work-stealing runtime, and Tower middleware.

## Production Rust Axum Service (`src/main.rs`)
```rust
use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use sqlx::{PgPool, postgres::PgPoolOptions};
use std::sync::Arc;
use tower_http::trace::TraceLayer;

#[derive(Clone)]
struct AppState {
    db: PgPool,
}

#[derive(Serialize, Deserialize, sqlx::FromRow)]
struct SkillRecord {
    id: String,
    name: String,
    trust_score: f64,
}

#[derive(Deserialize)]
struct CreateSkillRequest {
    name: String,
    trust_score: f64,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt::init();

    let database_url = std::env::var("DATABASE_URL").unwrap_or_else(|_| "postgres://localhost/skills".into());
    let pool = PgPoolOptions::new()
        .max_connections(50)
        .connect(&database_url)
        .await?;

    let state = Arc::new(AppState { db: pool });

    let app = Router::new()
        .route("/health", get(|| async { "OK" }))
        .route("/skills", post(create_skill).get(list_skills))
        .route("/skills/:id", get(get_skill))
        .layer(TraceLayer::new_for_http())
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await?;
    tracing::info!("Listening on {}", listener.local_addr()?);
    axum::serve(listener, app).await?;

    Ok(())
}

async fn get_skill(
    Path(id): Path<String>,
    State(state): State<Arc<AppState>>,
) -> Result<Json<SkillRecord>, StatusCode> {
    sqlx::query_as::<_, SkillRecord>("SELECT id, name, trust_score FROM skills WHERE id = $1")
        .bind(id)
        .fetch_optional(&state.db)
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?
        .map(Json)
        .ok_or(StatusCode::NOT_FOUND)
}

async fn create_skill(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<CreateSkillRequest>,
) -> Result<(StatusCode, Json<SkillRecord>), StatusCode> {
    let id = uuid::Uuid::new_v4().to_string();
    let record = sqlx::query_as::<_, SkillRecord>(
        "INSERT INTO skills (id, name, trust_score) VALUES ($1, $2, $3) RETURNING id, name, trust_score"
    )
    .bind(&id)
    .bind(&payload.name)
    .bind(payload.trust_score)
    .fetch_one(&state.db)
    .await
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok((StatusCode::CREATED, Json(record)))
}

async fn list_skills(
    State(state): State<Arc<AppState>>,
) -> Result<Json<Vec<SkillRecord>>, StatusCode> {
    let records = sqlx::query_as::<_, SkillRecord>("SELECT id, name, trust_score FROM skills ORDER BY trust_score DESC LIMIT 50")
        .fetch_all(&state.db)
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(records))
}
```

## Anti-Patterns
- ❌ Performing blocking CPU-heavy operations or synchronous file I/O directly in Tokio worker threads without `tokio::task::spawn_blocking`.
- ❌ Unbounded memory allocations in request body parsers (always enforce request body limits with `DefaultBodyLimit`).
"""
    }
]

