"""
Jumbos - Users Routes (Browse & Search Network)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import User, UserLocation, ZipCode, City, State
from app.schemas import UserProfile
from app.dependencies import get_current_user
from typing import Optional

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/search", response_model=list[UserProfile])
def search_users(
    q: Optional[str] = None,
    role: Optional[str] = None,
    state_code: Optional[str] = None,
    city: Optional[str] = None,
    zip_code: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Search users by name, role, and location.
    The location-first search is the core value prop of Jumbos.
    """
    query = db.query(User).filter(User.is_active == True)

    # Free text search on name
    if q:
        query = query.filter(User.full_name.ilike(f"%{q}%"))

    # Filter by role
    if role:
        query = query.filter(User.role == role)

    # Filter by location (ZIP code, city, or state)
    if zip_code:
        # Users who serve this ZIP code
        user_ids = db.query(UserLocation.user_id).filter(
            UserLocation.zip_code == zip_code
        ).subquery()
        query = query.filter(User.id.in_(user_ids))
    elif city:
        # Users who serve ZIP codes in this city
        zip_codes = db.query(ZipCode.code).filter(
            ZipCode.city_id == City.id,
            City.name.ilike(f"%{city}%")
        ).subquery()
        user_ids = db.query(UserLocation.user_id).filter(
            UserLocation.zip_code.in_(zip_codes)
        ).subquery()
        query = query.filter(User.id.in_(user_ids))
    elif state_code:
        # Users who serve ZIP codes in this state
        zip_codes = db.query(ZipCode.code).join(City).filter(
            City.state_code == state_code.upper()
        ).subquery()
        user_ids = db.query(UserLocation.user_id).filter(
            UserLocation.zip_code.in_(zip_codes)
        ).subquery()
        query = query.filter(User.id.in_(user_ids))

    # Exclude current user
    query = query.filter(User.id != current_user.id)

    # Paginate
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()

    return [UserProfile.model_validate(u) for u in users]


@router.get("/{user_id}", response_model=UserProfile)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a user's public profile."""
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfile.model_validate(user)


@router.get("/{user_id}/locations", response_model=list[dict])
def get_user_locations(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the locations a user serves (public info)."""
    locations = db.query(UserLocation).filter(UserLocation.user_id == user_id).all()
    result = []
    for loc in locations:
        zip_obj = db.query(ZipCode).filter(ZipCode.code == loc.zip_code).first()
        city_info = None
        state_info = None
        if zip_obj:
            city = db.query(City).filter(City.id == zip_obj.city_id).first()
            if city:
                state = db.query(State).filter(State.code == city.state_code).first()
                city_info = {"id": city.id, "name": city.name, "state_code": city.state_code}
                state_info = {"code": state.code, "name": state.name} if state else None
        result.append({
            "zip_code": loc.zip_code,
            "is_primary": loc.is_primary,
            "city": city_info,
            "state": state_info,
        })
    return result