"""
Jumbos - Location Routes (States, Cities, ZIP Codes)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import State, City, ZipCode, UserLocation
from app.schemas import StateInfo, CityInfo, ZipCodeInfo, UserLocationCreate, UserLocationResponse
from app.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/api/v1/locations", tags=["Locations"])


@router.get("/states", response_model=list[StateInfo])
def list_states(db: Session = Depends(get_db)):
    """List all US states."""
    states = db.query(State).order_by(State.name).all()
    return [StateInfo(code=s.code, name=s.name) for s in states]


@router.get("/states/{state_code}/cities", response_model=list[CityInfo])
def list_cities(state_code: str, db: Session = Depends(get_db)):
    """List cities in a state."""
    state = db.query(State).filter(State.code == state_code.upper()).first()
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    cities = db.query(City).filter(City.state_code == state_code.upper()).order_by(City.name).all()
    return [CityInfo(id=c.id, name=c.name, state_code=c.state_code, slug=c.slug) for c in cities]


@router.get("/cities/{city_id}/zipcodes", response_model=list[ZipCodeInfo])
def list_zipcodes(city_id: int, db: Session = Depends(get_db)):
    """List ZIP codes in a city."""
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    zips = db.query(ZipCode).filter(ZipCode.city_id == city_id).order_by(ZipCode.code).all()
    return [ZipCodeInfo(code=z.code, city_id=z.city_id) for z in zips]


@router.get("/zipcodes/{zip_code}", response_model=ZipCodeInfo)
def get_zipcode(zip_code: str, db: Session = Depends(get_db)):
    """Get ZIP code details."""
    z = db.query(ZipCode).filter(ZipCode.code == zip_code).first()
    if not z:
        raise HTTPException(status_code=404, detail="ZIP code not found")
    return ZipCodeInfo(code=z.code, city_id=z.city_id)


@router.get("/search", response_model=dict)
def search_locations(q: str = "", db: Session = Depends(get_db)):
    """Search locations by city name, state, or ZIP code."""
    results = {"states": [], "cities": [], "zip_codes": []}
    
    if len(q) >= 2:
        # Search states
        states = db.query(State).filter(State.name.ilike(f"%{q}%")).all()
        results["states"] = [StateInfo(code=s.code, name=s.name) for s in states]
        
        # Search cities
        cities = db.query(City).filter(City.name.ilike(f"%{q}%")).all()
        results["cities"] = [CityInfo(id=c.id, name=c.name, state_code=c.state_code, slug=c.slug) for c in cities]
        
        # Search ZIP codes
        zips = db.query(ZipCode).filter(ZipCode.code.ilike(f"{q}%")).all()
        results["zip_codes"] = [ZipCodeInfo(code=z.code, city_id=z.city_id) for z in zips]
    
    return results


# ─── User's Location Preferences ──────────────────────────────────────────────

@router.get("/me", response_model=list[UserLocationResponse])
def get_my_locations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's served locations."""
    locations = db.query(UserLocation).filter(UserLocation.user_id == current_user.id).all()
    result = []
    for loc in locations:
        loc_info = UserLocationResponse(
            id=loc.id,
            user_id=loc.user_id,
            zip_code=loc.zip_code,
            is_primary=loc.is_primary,
        )
        # Enrich with city/state info
        zip_obj = db.query(ZipCode).filter(ZipCode.code == loc.zip_code).first()
        if zip_obj:
            city = db.query(City).filter(City.id == zip_obj.city_id).first()
            if city:
                state = db.query(State).filter(State.code == city.state_code).first()
                loc_info.city = CityInfo(id=city.id, name=city.name, state_code=city.state_code, slug=city.slug) if city else None
                loc_info.state = StateInfo(code=state.code, name=state.name) if state else None
        result.append(loc_info)
    return result


@router.post("/me", response_model=UserLocationResponse, status_code=201)
def add_my_location(
    req: UserLocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a location the user serves."""
    # Validate ZIP exists
    zip_obj = db.query(ZipCode).filter(ZipCode.code == req.zip_code).first()
    if not zip_obj:
        raise HTTPException(status_code=404, detail="ZIP code not found")
    
    # Check for duplicate
    existing = db.query(UserLocation).filter(
        UserLocation.user_id == current_user.id,
        UserLocation.zip_code == req.zip_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Location already added")
    
    loc = UserLocation(
        user_id=current_user.id,
        zip_code=req.zip_code,
        is_primary=req.is_primary,
    )
    # If setting as primary, unset other primaries
    if req.is_primary:
        db.query(UserLocation).filter(
            UserLocation.user_id == current_user.id,
            UserLocation.is_primary == True,
        ).update({"is_primary": False})
    
    db.add(loc)
    db.commit()
    db.refresh(loc)
    
    return UserLocationResponse(
        id=loc.id,
        user_id=loc.user_id,
        zip_code=loc.zip_code,
        is_primary=loc.is_primary,
    )


@router.delete("/me/{location_id}", status_code=204)
def remove_my_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a location the user serves."""
    loc = db.query(UserLocation).filter(
        UserLocation.id == location_id,
        UserLocation.user_id == current_user.id,
    ).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(loc)
    db.commit()