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

# 1. Domain Entity
@dataclass(frozen=True)
class User:
    id: str
    email: str
    is_active: bool

# 2. Port (Interface)
class UserRepositoryPort(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def save(self, user: User) -> None:
        pass

# 3. Use Case
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

## Anti-Patterns
- ❌ Attempting full 'Big-Bang' rewrites that halt business delivery for months and fail in production cutovers.
- ❌ Refactoring complex legacy logic without golden master characterization tests.
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
"""
    }
]
