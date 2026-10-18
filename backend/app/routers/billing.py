from typing import Annotated

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import CurrentUser
from app.models.database import get_db
from app.models.schemas import Subscription

router = APIRouter(prefix="/api/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    success_url: str = "http://localhost:3000/billing?status=success"
    cancel_url: str = "http://localhost:3000/billing?status=canceled"


class CheckoutResponse(BaseModel):
    url: str


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    user: CurrentUser, body: CheckoutRequest, db: Annotated[AsyncSession, Depends(get_db)]
):
    if not settings.stripe_secret_key:
        raise HTTPException(400, "Stripe is not configured on the server")
    if user.tenant_id is None:
        raise HTTPException(400, "No tenant associated with user")

    from sqlalchemy import select

    from app.models.schemas import Tenant

    tenant = (
        await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    ).scalar_one()

    if not tenant.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            metadata={"tenant_id": str(tenant.id)},
        )
        tenant.stripe_customer_id = customer.id
        await db.commit()

    session = stripe.checkout.Session.create(
        customer=tenant.stripe_customer_id,
        payment_mode="subscription",
        line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
        success_url=body.success_url,
        cancel_url=body.cancel_url,
        subscription_data={"metadata": {"tenant_id": str(tenant.id)}},
        client_reference_id=str(user.id),
    )
    return CheckoutResponse(url=session.url)


@router.get("/status")
async def subscription_status(
    user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]
):
    from sqlalchemy import select

    sub = (
        await db.execute(
            select(Subscription)
            .where(Subscription.tenant_id == user.tenant_id)
            .limit(1)
        )
    ).scalar_one_or_none()
    if sub is None:
        return {"active": False, "plan": "free", "status": None}
    return {
        "active": sub.status in ("active", "trialing"),
        "plan": sub.plan,
        "status": sub.status,
    }


@router.post("/webhook")
async def stripe_webhook(request: Request):
    if not settings.stripe_webhook_secret:
        raise HTTPException(400, "Stripe webhook secret not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header or "", settings.stripe_webhook_secret
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    # Persist state changes here (e.g., subscription updates)
    event_type = event["type"]
    data = event["data"]["object"]

    # Forward to worker / update DB in production
    return {"received": True, "event_type": event_type}
