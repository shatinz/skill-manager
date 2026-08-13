---
id: business-ecommerce-growth.marketplace-apis.torob-marketplace-integration
name: torob-marketplace-integration
title: Torob Marketplace API Integration & Price Feed Sync
category: business-ecommerce-growth
subcategory: marketplace-apis
version: 1.2.0
tags:
- torob
- marketplace
- price-comparison
- e-commerce
- api
- feed-sync
- crawler
trust_rating: 0.95
estimated_tokens: 1500
description: Integrate with the Torob price comparison marketplace API, serving structured
  product feeds, real-time price/availability updates, and crawler optimization.
trigger_patterns:
- torob api integration feed
- torob price comparison webhook
- ecommerce product feed torob format
- sync inventory price torob
---

# Torob Marketplace API Integration & Price Feed Sync

## Objective
Connect e-commerce platforms to Torob's price-comparison engine via standard JSON product feeds and real-time inventory/price synchronization endpoints.

## Production Torob Feed Endpoint (`routers/torob.py`)
```python
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/marketplace/torob", tags=["Torob"])

class TorobProduct(BaseModel):
    page_unique_id: str
    title: str
    price: int  # in Tomans / Rials
    availability: bool
    page_url: str
    image_url: Optional[str]
    old_price: Optional[int]

@router.get("/products", response_model=List[TorobProduct])
async def get_torob_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, le=500)
):
    products = await product_service.get_in_stock_catalog(page=page, page_size=page_size)
    return [
        TorobProduct(
            page_unique_id=str(p.id),
            title=p.title,
            price=int(p.current_price),
            availability=p.stock_count > 0,
            page_url=f"https://example.com/p/{p.slug}",
            image_url=p.main_image_url,
            old_price=int(p.original_price) if p.original_price > p.current_price else None
        )
        for p in products
    ]
```

## Anti-Patterns
- ❌ Serving stale cached price feeds to Torob crawlers, triggering marketplace penalty delistings.
