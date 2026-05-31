"""
Jumbos - Pydantic Schemas (Request/Response Models)
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ─── Auth ──────────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=150)
    role: str = "agent"  # defaults to agent
    phone: Optional[str] = None
    company_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserProfile"


# ─── User ──────────────────────────────────────────────────────────────────────
class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    headline: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    profile_image_url: Optional[str] = None
    company_name: Optional[str] = None
    role: str
    subscription_tier: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=150)
    headline: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    profile_image_url: Optional[str] = None
    company_name: Optional[str] = None
    role: Optional[str] = None


# ─── Locations ─────────────────────────────────────────────────────────────────
class StateInfo(BaseModel):
    code: str
    name: str


class CityInfo(BaseModel):
    id: int
    name: str
    state_code: str
    slug: str


class ZipCodeInfo(BaseModel):
    code: str
    city_id: int


class UserLocationCreate(BaseModel):
    zip_code: str
    is_primary: bool = False


class UserLocationResponse(BaseModel):
    id: int
    user_id: str
    zip_code: str
    is_primary: bool
    city: Optional[CityInfo] = None
    state: Optional[StateInfo] = None

    class Config:
        from_attributes = True


# ─── Connections ──────────────────────────────────────────────────────────────
class ConnectionRequest(BaseModel):
    addressee_id: str


class ConnectionResponse(BaseModel):
    id: int
    requester_id: str
    addressee_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    requester: Optional[UserProfile] = None
    addressee: Optional[UserProfile] = None

    class Config:
        from_attributes = True


# ─── Messages ──────────────────────────────────────────────────────────────────
class MessageSendRequest(BaseModel):
    recipient_id: str
    subject: Optional[str] = Field(None, max_length=255)
    body: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: str
    sender_id: str
    recipient_id: str
    subject: Optional[str] = None
    body: str
    status: str
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Deals ─────────────────────────────────────────────────────────────────────
class DealCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    deal_type: str
    state_code: str = Field(..., min_length=2, max_length=2)
    city_id: Optional[int] = None
    zip_code: Optional[str] = None
    address: Optional[str] = None
    price: Optional[float] = None
    square_feet: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    property_type: Optional[str] = None
    tags: Optional[List[str]] = None
    media_urls: Optional[List[str]] = None
    expires_at: Optional[datetime] = None


class DealUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    status: Optional[str] = None
    price: Optional[float] = None
    square_feet: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    tags: Optional[List[str]] = None


class DealResponse(BaseModel):
    id: str
    creator_id: str
    title: str
    description: str
    deal_type: str
    status: str
    state_code: str
    city_id: Optional[int] = None
    zip_code: Optional[str] = None
    address: Optional[str] = None
    price: Optional[float] = None
    square_feet: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    property_type: Optional[str] = None
    tags: Optional[List[str]] = None
    media_urls: Optional[List[str]] = None
    views_count: int
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    creator: Optional[UserProfile] = None

    class Config:
        from_attributes = True


class DealSearchParams(BaseModel):
    query: Optional[str] = None
    deal_type: Optional[str] = None
    state_code: Optional[str] = None
    city_id: Optional[int] = None
    zip_code: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    property_type: Optional[str] = None
    min_bedrooms: Optional[int] = None
    status: Optional[str] = "active"
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


# ─── Pagination ────────────────────────────────────────────────────────────────
class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    per_page: int
    total_pages: int


# ─── Subscription ─────────────────────────────────────────────────────────────
class SubscriptionUpgradeRequest(BaseModel):
    tier: str = "premium"


class SubscriptionResponse(BaseModel):
    user_id: str
    subscription_tier: str
    features: List[str]