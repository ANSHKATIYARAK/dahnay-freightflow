"""
SaaS Platform: Billing, Stripe Webhooks & Subscription Metering
Handles subscription tiers, credit packs, usage metering, and Stripe webhook lifecycle events.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
from saas_platform.models import DatabaseManager, Workspace


PLANS = {
    "free": {"name": "Free Tier", "credits": 20, "price_usd": 0, "max_monitors": 1},
    "starter": {"name": "Starter Agent Pack", "credits": 500, "price_usd": 49, "max_monitors": 10},
    "pro": {"name": "Pro Studio Retainer", "credits": 2500, "price_usd": 149, "max_monitors": 50},
    "enterprise": {"name": "Enterprise Dedicated", "credits": 10000, "price_usd": 499, "max_monitors": 250}
}


class BillingManager:
    """Manages Stripe subscription events and usage-based credit refills."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def handle_stripe_webhook(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes real or simulated Stripe webhook events:
        - checkout.session.completed
        - customer.subscription.updated
        - invoice.payment_succeeded
        """
        data = payload.get("data", {}).get("object", {})
        customer_id = data.get("customer")
        
        if event_type == "checkout.session.completed":
            # e.g., credit pack purchased or subscription started
            workspace_id = data.get("client_reference_id")
            plan_selected = data.get("metadata", {}).get("plan", "starter")
            credits_to_add = PLANS.get(plan_selected, {}).get("credits", 500)
            
            if workspace_id:
                self.db.add_credits(workspace_id, credits_to_add)
                return {"status": "success", "action": "credits_added", "amount": credits_to_add, "workspace_id": workspace_id}

        elif event_type == "invoice.payment_succeeded":
            # Monthly renewal refill
            return {"status": "success", "action": "subscription_renewed", "customer_id": customer_id}

        return {"status": "ignored", "event_type": event_type}

    def check_has_credits(self, workspace_id: str, required_credits: int = 1) -> bool:
        ws = self.db.get_workspace(workspace_id)
        if not ws:
            return False
        return ws.credits_balance >= required_credits
