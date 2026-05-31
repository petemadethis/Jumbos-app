"""
Jumbos - Subscription Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, SubscriptionTier
from app.schemas import SubscriptionUpgradeRequest, SubscriptionResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/subscription", tags=["Subscription"])


PREMIUM_FEATURES = [
    "Send direct messages to any connected user",
    "Post and manage deal listings",
    "Interact with deal listings (save, inquire)",
    "Unlimited connections",
    "Priority support",
    "Advanced network analytics",
]

FREE_FEATURES = [
    "Browse the professional network",
    "View user profiles",
    "Explore deal listings (read-only)",
    "Receive connection requests",
    "Receive messages from connected users",
]


@router.get("/", response_model=SubscriptionResponse)
def get_subscription(
    current_user: User = Depends(get_current_user),
):
    """Get the current user's subscription details."""
    features = PREMIUM_FEATURES if current_user.subscription_tier == SubscriptionTier.PREMIUM else FREE_FEATURES
    return SubscriptionResponse(
        user_id=current_user.id,
        subscription_tier=current_user.subscription_tier.value,
        features=features,
    )


@router.get("/plans")
def list_plans():
    """List available subscription plans."""
    return {
        "plans": [
            {
                "tier": "free",
                "name": "Free",
                "price": 0,
                "features": FREE_FEATURES,
            },
            {
                "tier": "premium",
                "name": "Premium",
                "price": 19.99,
                "features": PREMIUM_FEATURES,
                "note": "Monthly subscription. Cancel anytime.",
            },
        ]
    }


@router.post("/upgrade", response_model=SubscriptionResponse)
def upgrade_subscription(
    req: SubscriptionUpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upgrade or downgrade subscription tier."""
    try:
        new_tier = SubscriptionTier(req.tier)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid tier")

    if current_user.subscription_tier == new_tier:
        raise HTTPException(status_code=400, detail=f"Already on {new_tier.value} plan")

    current_user.subscription_tier = new_tier
    db.commit()
    db.refresh(current_user)

    features = PREMIUM_FEATURES if new_tier == SubscriptionTier.PREMIUM else FREE_FEATURES
    return SubscriptionResponse(
        user_id=current_user.id,
        subscription_tier=current_user.subscription_tier.value,
        features=features,
    )