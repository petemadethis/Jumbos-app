"""
Jumbos - Deal Marketplace Routes
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import (
    User, Deal, DealStatus, DealType, DealInteraction,
    UserLocation, ZipCode, City, State
)
from app.schemas import (
    DealCreateRequest, DealUpdateRequest, DealResponse, DealSearchParams
)
from app.dependencies import get_current_user, require_premium

router = APIRouter(prefix="/api/v1/deals", tags=["Deals"])


@router.get("/", response_model=dict)
def list_deals(
    deal_type: str = None,
    state_code: str = None,
    city_id: int = None,
    zip_code: str = None,
    status: str = "active",
    min_price: float = None,
    max_price: float = None,
    property_type: str = None,
    min_bedrooms: int = None,
    q: str = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Browse deal listings with location-first filtering."""
    query = db.query(Deal)

    # Filter by status
    if status:
        try:
            status_enum = DealStatus(status)
            query = query.filter(Deal.status == status_enum)
        except ValueError:
            pass

    # Filter by deal type
    if deal_type:
        try:
            type_enum = DealType(deal_type)
            query = query.filter(Deal.deal_type == type_enum)
        except ValueError:
            pass

    # Location filters (core feature)
    if zip_code:
        query = query.filter(Deal.zip_code == zip_code)
    elif city_id:
        zip_codes = db.query(ZipCode.code).filter(ZipCode.city_id == city_id).subquery()
        query = query.filter(Deal.zip_code.in_(zip_codes))
    elif state_code:
        query = query.filter(Deal.state_code == state_code.upper())

    # Price range
    if min_price is not None:
        query = query.filter(Deal.price >= min_price)
    if max_price is not None:
        query = query.filter(Deal.price <= max_price)

    # Property type
    if property_type:
        query = query.filter(Deal.property_type == property_type)

    # Min bedrooms
    if min_bedrooms is not None:
        query = query.filter(Deal.bedrooms >= min_bedrooms)

    # Text search
    if q:
        query = query.filter(
            Deal.title.ilike(f"%{q}%") | Deal.description.ilike(f"%{q}%")
        )

    # Order by most recent
    query = query.order_by(desc(Deal.created_at))

    # Paginate
    total = query.count()
    deals = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": [DealResponse.model_validate(d) for d in deals],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if total > 0 else 0,
    }


@router.get("/my", response_model=list[DealResponse])
def my_deals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the current user's deal listings."""
    deals = db.query(Deal).filter(Deal.creator_id == current_user.id).order_by(desc(Deal.created_at)).all()
    return [DealResponse.model_validate(d) for d in deals]


@router.get("/{deal_id}", response_model=DealResponse)
def get_deal(
    deal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single deal listing."""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    # Increment view count
    deal.views_count += 1
    db.commit()

    return DealResponse.model_validate(deal)


@router.post("/", response_model=DealResponse, status_code=201)
def create_deal(
    req: DealCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new deal listing. Premium subscription required."""
    from app.models import SubscriptionTier
    if current_user.subscription_tier != SubscriptionTier.PREMIUM:
        raise HTTPException(
            status_code=403,
            detail="Premium subscription required to post deals",
        )

    # Validate deal type
    try:
        deal_type = DealType(req.deal_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid deal type. Must be one of: {[d.value for d in DealType]}",
        )

    # Validate state
    state = db.query(State).filter(State.code == req.state_code.upper()).first()
    if not state:
        raise HTTPException(status_code=400, detail="Invalid state code")

    deal = Deal(
        id=str(uuid.uuid4()),
        creator_id=current_user.id,
        title=req.title,
        description=req.description,
        deal_type=deal_type,
        status=DealStatus.ACTIVE,
        state_code=req.state_code.upper(),
        city_id=req.city_id,
        zip_code=req.zip_code,
        address=req.address,
        price=req.price,
        square_feet=req.square_feet,
        bedrooms=req.bedrooms,
        bathrooms=req.bathrooms,
        property_type=req.property_type,
        tags=req.tags,
        media_urls=req.media_urls,
        expires_at=req.expires_at,
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)
    return DealResponse.model_validate(deal)


@router.patch("/{deal_id}", response_model=DealResponse)
def update_deal(
    deal_id: str,
    req: DealUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a deal listing (own deals only)."""
    deal = db.query(Deal).filter(
        Deal.id == deal_id,
        Deal.creator_id == current_user.id,
    ).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found or not yours")

    update_data = req.model_dump(exclude_unset=True)
    if "status" in update_data:
        try:
            update_data["status"] = DealStatus(update_data["status"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")

    for field, value in update_data.items():
        setattr(deal, field, value)

    db.commit()
    db.refresh(deal)
    return DealResponse.model_validate(deal)


@router.delete("/{deal_id}", status_code=204)
def delete_deal(
    deal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a deal listing (own deals only)."""
    deal = db.query(Deal).filter(
        Deal.id == deal_id,
        Deal.creator_id == current_user.id,
    ).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found or not yours")
    db.delete(deal)
    db.commit()


@router.post("/{deal_id}/interact")
def interact_with_deal(
    deal_id: str,
    interaction_type: str = Query(...),
    note: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Interact with a deal (save, inquiry, etc.)."""
    if interaction_type not in ("save", "inquiry", "share"):
        raise HTTPException(status_code=400, detail="Invalid interaction type")

    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    interaction = DealInteraction(
        user_id=current_user.id,
        deal_id=deal_id,
        interaction_type=interaction_type,
        note=note,
    )
    db.add(interaction)
    db.commit()
    return {"status": "ok", "interaction_type": interaction_type}


@router.get("/{deal_id}/interactions/count")
def deal_interaction_counts(
    deal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get interaction counts for a deal."""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    from sqlalchemy import func
    counts = (
        db.query(DealInteraction.interaction_type, func.count(DealInteraction.id))
        .filter(DealInteraction.deal_id == deal_id)
        .group_by(DealInteraction.interaction_type)
        .all()
    )
    return {row[0]: row[1] for row in counts}