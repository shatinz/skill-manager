# FastAPI Production Architecture & Async Engineering

## Objective
Design high-throughput, maintainable, and type-safe async REST APIs using FastAPI, Pydantic v2, and SQLAlchemy 2.0 with clean layered architecture (Routers -> Services -> Repositories -> Models).

## Architectural Guidelines
1. **Layered Structure**: Routers handle HTTP parsing, status codes, and dependency injection. Services handle business logic and orchestration. Repositories handle database I/O.
2. **Lifespan Context**: Use `@asynccontextmanager` lifespan handlers for startup/shutdown (connection pools, Redis, Kafka clients) instead of deprecated `on_event`.
3. **Pydantic v2 Strictness**: Use `model_validate`, `model_dump`, and `ConfigDict(from_attributes=True)` for serialization.
4. **RFC 7807 Problem Details**: Structure all error responses with `type`, `title`, `status`, `detail`, and `instance`.

## Production Blueprint

### Service Layer & Router (`routers/orders.py`)
```python
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import uuid

# Lifespan and Engine
DATABASE_URL = "postgresql+asyncpg://postgres:secret@localhost:5432/appdb"
engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=10)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

DbSession = Annotated[AsyncSession, Depends(get_db_session)]

# Schemas
class OrderCreate(BaseModel):
    customer_email: str = Field(..., max_length=255)
    sku: str = Field(..., min_length=3, max_length=50)
    quantity: int = Field(1, ge=1, le=100)

class OrderResponse(BaseModel):
    id: uuid.UUID
    customer_email: str
    sku: str
    quantity: int
    status: str
    model_config = ConfigDict(from_attributes=True)

# Router
router = APIRouter(prefix="/v1/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, db: DbSession):
    order = await order_service.place_order(db=db, payload=payload)
    return order

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: uuid.UUID, db: DbSession):
    order = await order_service.get_order(db=db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found."
        )
    return order
```

## Anti-Patterns & Traps
- ❌ **Blocking Calls in Async Def**: Running `requests.get()` or `time.sleep()` in `async def` endpoints locks the event loop. Use `httpx.AsyncClient` or `asyncio.sleep`.
- ❌ **Direct ORM Exposure**: Returning SQLAlchemy models without Pydantic conversion causes memory leaks, circular serialization, and secret exposure.
- ❌ **Missing Async Commit/Rollback**: Failing to use session context managers leaves uncommitted transactions dangling in connection pools.

## Verification
- [ ] Execute `pytest-asyncio` test suite with `httpx.AsyncClient(transport=ASGITransport(app=app))` fixture.
- [ ] Profile concurrent throughput with `wrk` or `locust` to verify no event-loop blocking.