---
id: business-ecommerce-growth.marketplace-apis.divar-marketplace-automation
name: divar-marketplace-automation
title: Divar Marketplace OAuth2 API & Listing Automation
category: business-ecommerce-growth
subcategory: marketplace-apis
version: 1.2.0
tags:
- divar
- marketplace
- oauth2
- listing-automation
- iran-tech
- api-integration
trust_rating: 0.95
estimated_tokens: 1500
description: Automate listing creation, inquiry management, and OAuth2 authorization
  on the Divar Open Platform marketplace API.
trigger_patterns:
- divar api open platform integration
- divar listing automation oauth2
- divar marketplace webhook
- divar post creation api
---

# Divar Marketplace OAuth2 API & Listing Automation

## Objective
Connect enterprise systems to the Divar Open Platform to automate posting listings, managing user queries, and tracking marketplace lead conversions.

## OAuth2 & Listing API Blueprint (`services/divar.py`)
```python
import httpx

DIVAR_API_BASE = "https://open-api.divar.ir"

class DivarClient:
    def __init__(self, api_key: str, access_token: str):
        self.headers = {
            "x-api-key": api_key,
            "x-access-token": access_token,
            "Content-Type": "application/json"
        }

    async def create_user_post(self, post_data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{DIVAR_API_BASE}/v1/open-platform/post/create",
                json=post_data,
                headers=self.headers,
                timeout=10.0
            )
            res.raise_for_status()
            return res.json()
```

## Anti-Patterns
- ❌ Hardcoding unrefreshed user access tokens without handling 401 token refresh cycles.
