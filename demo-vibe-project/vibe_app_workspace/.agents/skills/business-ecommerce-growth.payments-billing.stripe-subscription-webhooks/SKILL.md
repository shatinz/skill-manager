# Stripe Subscription Lifecycle & Webhook Verification

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