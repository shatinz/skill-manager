"""
Category 8: Business, E-Commerce & Growth (5 Skills)
"""

BUSINESS_ECOMMERCE_SKILLS = [
    {
        "id": "business-ecommerce-growth.payments-billing.stripe-subscription-webhooks",
        "name": "stripe-subscription-webhooks",
        "title": "Stripe Subscription Lifecycle, Webhook Verification & Checkout",
        "category": "business-ecommerce-growth",
        "subcategory": "payments-billing",
        "version": "1.4.0",
        "tags": ["stripe", "payments", "subscriptions", "webhooks", "checkout", "billing", "saas"],
        "trust_rating": 0.99,
        "estimated_tokens": 1650,
        "description": "Implement end-to-end SaaS recurring billing with Stripe Checkout Sessions, cryptographic webhook signature verification, and subscription state machines.",
        "trigger_patterns": [
            "stripe subscription checkout session",
            "stripe webhook signature verification",
            "handle stripe customer.subscription.updated",
            "stripe customer portal integration"
        ],
        "content": """# Stripe Subscription Lifecycle & Webhook Verification

## Objective
Implement resilient recurring SaaS monetization workflows with Stripe Checkout, customer billing portals, and idempotent raw-body webhook signature verification.

## Production Webhook Handler (`api/webhooks/stripe.py`)
```python
import stripe
from fastapi import APIRouter, Request, Header, HTTPException, status
from app.services.billing import update_subscription_status

router = APIRouter(prefix="/webhooks/stripe")
STRIPE_WEBHOOK_SECRET = "whsec_xxxxxxxx"

@router.post("/")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    data_object = event["data"]["object"]

    if event_type in ("customer.subscription.created", "customer.subscription.updated"):
        await update_subscription_status(
            stripe_customer_id=data_object["customer"],
            status=data_object["status"],
            plan_id=data_object["items"]["data"][0]["plan"]["id"]
        )
    elif event_type == "customer.subscription.deleted":
        await update_subscription_status(
            stripe_customer_id=data_object["customer"],
            status="canceled"
        )

    return {"status": "success"}
```

## Anti-Patterns
- ❌ Parsing JSON body before validating the raw payload bytes against the Stripe signature.
"""
    },

    {
        "id": "business-ecommerce-growth.seo-growth.open-seo-audit-engine",
        "name": "open-seo-audit-engine",
        "title": "Technical SEO Engine, OpenGraph & Core Web Vitals",
        "category": "business-ecommerce-growth",
        "subcategory": "seo-growth",
        "version": "1.3.0",
        "tags": ["seo", "opengraph", "core-web-vitals", "sitemap", "json-ld", "meta-tags"],
        "trust_rating": 0.98,
        "estimated_tokens": 1550,
        "description": "Optimize web platforms for search engine visibility with JSON-LD structured data schemas, dynamic OpenGraph image generators, XML sitemaps, and Core Web Vitals tuning.",
        "trigger_patterns": [
            "technical seo json-ld structured data",
            "dynamic opengraph image generation",
            "xml sitemap robots.txt nextjs",
            "core web vitals lcp cls optimization"
        ],
        "content": """# Technical SEO Engine, OpenGraph & Core Web Vitals

## Objective
Maximize organic search indexing and social click-through rates by automating schema.org JSON-LD microdata, OpenGraph cards, and Core Web Vitals performance.

## Dynamic JSON-LD & Metadata Blueprint (`app/products/[id]/page.tsx`)
```tsx
import type { Metadata } from 'next';

export async function generateMetadata({ params }: { params: { id: string } }): Promise<Metadata> {
  const product = await getProduct(params.id);
  return {
    title: `${product.title} | E-Store`,
    description: product.description,
    openGraph: {
      title: product.title,
      description: product.description,
      images: [{ url: `/api/og?title=${encodeURIComponent(product.title)}` }],
    },
    alternates: {
      canonical: `https://example.com/products/${params.id}`,
    },
  };
}

export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await getProduct(params.id);
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.title,
    description: product.description,
    offers: {
      '@type': 'Offer',
      price: product.price,
      priceCurrency: 'USD',
      availability: 'https://schema.org/InStock',
    },
  };

  return (
    <main>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <h1>{product.title}</h1>
    </main>
  );
}
```

## Anti-Patterns
- ❌ Missing canonical URL tags, resulting in search engine duplicate content penalties.
"""
    },

    {
        "id": "business-ecommerce-growth.marketplace-apis.torob-marketplace-integration",
        "name": "torob-marketplace-integration",
        "title": "Torob Marketplace API Integration & Price Feed Sync",
        "category": "business-ecommerce-growth",
        "subcategory": "marketplace-apis",
        "version": "1.2.0",
        "tags": ["torob", "marketplace", "price-comparison", "e-commerce", "api", "feed-sync", "crawler"],
        "trust_rating": 0.95,
        "estimated_tokens": 1500,
        "description": "Integrate with the Torob price comparison marketplace API, serving structured product feeds, real-time price/availability updates, and crawler optimization.",
        "trigger_patterns": [
            "torob api integration feed",
            "torob price comparison webhook",
            "ecommerce product feed torob format",
            "sync inventory price torob"
        ],
        "content": """# Torob Marketplace API Integration & Price Feed Sync

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
"""
    },

    {
        "id": "business-ecommerce-growth.chat-automation.telegram-bot-agent-controller",
        "name": "telegram-bot-agent-controller",
        "title": "Telegram Bot Agent Controller & AI Webhook Engine",
        "category": "business-ecommerce-growth",
        "subcategory": "chat-automation",
        "version": "1.3.0",
        "tags": ["telegram-bot", "ai-agent", "webhooks", "python-telegram-bot", "aiogram", "bot-father"],
        "trust_rating": 0.97,
        "estimated_tokens": 1600,
        "description": "Construct high-throughput Telegram AI bot controllers using webhooks, state machines, inline keyboard callbacks, and streaming LLM agent integrations.",
        "trigger_patterns": [
            "telegram bot ai agent webhook",
            "aiogram python telegram bot",
            "telegram inline keyboard callback",
            "stream ai response telegram bot"
        ],
        "content": """# Telegram Bot Agent Controller & AI Webhook Engine

## Objective
Build responsive, high-concurrency Telegram bot controllers using webhook architectures, inline interactive callbacks, and streaming AI agent task automation.

## Webhook Bot Controller (`telegram_agent.py`)
```python
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Run Agent Task", callback_data="run_task")],
        [InlineKeyboardButton(text="📊 View Metrics", callback_data="view_metrics")]
    ])
    await message.answer("Agentic Controller Active. Choose an action:", reply_markup=keyboard)

@dp.callback_query(F.data == "run_task")
async def handle_task_trigger(callback: types.CallbackQuery):
    await callback.answer("Task dispatched to LLM agent cluster...")
    await callback.message.edit_text("⏳ Processing agent task in background...")
```

## Anti-Patterns
- ❌ Using synchronous long-polling in production deployments instead of verified webhooks.
"""
    },

    {
        "id": "business-ecommerce-growth.marketplace-apis.divar-marketplace-automation",
        "name": "divar-marketplace-automation",
        "title": "Divar Marketplace OAuth2 API & Listing Automation",
        "category": "business-ecommerce-growth",
        "subcategory": "marketplace-apis",
        "version": "1.2.0",
        "tags": ["divar", "marketplace", "oauth2", "listing-automation", "iran-tech", "api-integration"],
        "trust_rating": 0.95,
        "estimated_tokens": 1500,
        "description": "Automate listing creation, inquiry management, and OAuth2 authorization on the Divar Open Platform marketplace API.",
        "trigger_patterns": [
            "divar api open platform integration",
            "divar listing automation oauth2",
            "divar marketplace webhook",
            "divar post creation api"
        ],
        "content": """# Divar Marketplace OAuth2 API & Listing Automation

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
"""
    }
]
