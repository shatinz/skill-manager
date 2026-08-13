---
id: web-frameworks.python-api.django-ninja-crud
name: django-ninja-crud
title: Django Ninja Type-Safe Async REST & Schema Craft
category: web-frameworks
subcategory: python-api
version: 1.2.0
tags:
- django-ninja
- django
- pydantic
- async
- rest-api
- python
trust_rating: 0.94
estimated_tokens: 1400
description: Build high-speed, type-safe REST APIs in Django using Django Ninja with
  Pydantic schemas, async ORM queries, authentication guards, and automatic OpenAPI
  generation.
trigger_patterns:
- django ninja rest api
- django ninja async crud
- django ninja pydantic schemas
- django ninja auth tokens
---

# Django Ninja Type-Safe Async REST & Schema Craft

## Objective
Develop type-safe, high-performance REST APIs within the Django ecosystem utilizing Django Ninja, Pydantic schemas, and asynchronous querysets.

## Blueprint (`api/views.py`)
```python
from ninja import NinjaAPI, Schema, ModelSchema
from ninja.pagination import paginate, PageNumberPagination
from ninja.security import HttpBearer
from typing import List
from django.shortcuts import aget_object_or_404
from .models import Product

api = NinjaAPI(title="Commerce Engine API", version="1.0.0")

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token == "super-secret-token":
            return {"username": "admin_agent"}
        return None

class ProductIn(Schema):
    title: str
    price: float
    sku: str
    in_stock: bool = True

class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'sku', 'in_stock', 'created_at']

@api.get("/products", response=List[ProductOut])
@paginate(PageNumberPagination, page_size=20)
async def list_products(request):
    return [p async for p in Product.objects.filter(in_stock=True).order_by('-created_at')]

@api.post("/products", response={201: ProductOut}, auth=AuthBearer())
async def create_product(request, payload: ProductIn):
    product = await Product.objects.acreate(**payload.dict())
    return 201, product
```

## Anti-Patterns
- ❌ Running synchronous ORM queries inside `async def` endpoints without `sync_to_async` or async ORM helpers (`acreate`, `aget_object_or_404`).
