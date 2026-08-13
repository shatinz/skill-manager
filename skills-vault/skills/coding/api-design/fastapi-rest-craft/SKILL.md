---
id: coding.api-design.fastapi-rest-craft
name: fastapi-rest-craft
title: FastAPI REST API Production Craft
category: coding
subcategory: api-design
version: 1.2.0
tags:
- fastapi
- python
- pydantic
- rest-api
- crud
- openapi
trust_rating: 0.96
estimated_tokens: 1400
description: Architect, implement, and harden production-grade FastAPI REST services
  with Pydantic v2 schemas, async database sessions, dependency injection, and standardized
  RFC 7807 error envelopes.
trigger_patterns:
- create a fastapi backend
- build rest api with fastapi
- fastapi crud endpoints
- pydantic v2 models for fastapi
- async sqlalchemy fastapi
---

# FastAPI REST API Production Craft

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
