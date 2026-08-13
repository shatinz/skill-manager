---
id: clean-architecture-refactoring.principles-patterns.dry-solid-clean-architecture
name: dry-solid-clean-architecture
title: DRY, SOLID Principles & Clean Hexagonal Architecture
category: clean-architecture-refactoring
subcategory: principles-patterns
version: 1.4.0
tags:
- solid
- dry
- clean-architecture
- hexagonal-architecture
- domain-driven-design
- refactoring
trust_rating: 0.99
estimated_tokens: 1700
description: Refactor monolithic and tightly-coupled codebases into Clean Hexagonal
  Architecture adhering to SOLID and DRY principles with decoupled domain entities,
  ports, and adapters.
trigger_patterns:
- clean architecture refactoring solid
- hexagonal architecture ports and adapters
- dependency inversion python typescript
- dry solid principles code review
---

# DRY, SOLID Principles & Clean Hexagonal Architecture

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
