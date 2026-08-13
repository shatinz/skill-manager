---
id: clean-architecture-refactoring.architecture-patterns.event-driven-cqrs-messaging
name: event-driven-cqrs-messaging
title: Command Query Responsibility Segregation (CQRS) & Event-Driven Messaging
category: clean-architecture-refactoring
subcategory: architecture-patterns
version: 1.3.0
tags:
- cqrs
- event-driven
- message-bus
- event-sourcing
- outbox-pattern
- rabbitmq
- kafka
trust_rating: 0.97
estimated_tokens: 1650
description: Architect scalable event-driven systems decoupling read and write models
  via CQRS, Transactional Outbox pattern, and idempotent event consumer handlers.
trigger_patterns:
- cqrs event driven architecture
- transactional outbox pattern postgres
- idempotent event consumer message bus
- event sourcing command query separation
---

# Command Query Responsibility Segregation (CQRS) & Event-Driven Messaging

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
