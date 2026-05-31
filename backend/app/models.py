"""
Jumbos - Database Schema & Models
A location-first real estate networking platform
"""

import os
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    create_engine, Column, String, Text, Integer, Float, Boolean,
    DateTime, ForeignKey, Enum, Index, UniqueConstraint, JSON
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.dialects.sqlite import TEXT as SQLITE_TEXT
import enum


# ─── Database Engine ──────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jumbos.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)


# ─── Declarative Base ─────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ─── Enums ────────────────────────────────────────────────────────────────────
class UserRole(str, enum.Enum):
    AGENT = "agent"
    BROKER = "broker"
    INVESTOR = "investor"
    WHOLESALER = "wholesaler"
    CONTRACTOR = "contractor"
    MORTGAGE_BROKER = "mortgage_broker"
    HARD_MONEY_LENDER = "hard_money_lender"
    PROPERTY_MANAGER = "property_manager"
    TITLE_COMPANY = "title_company"
    INSPECTOR = "inspector"
    INSURANCE = "insurance"
    ATTORNEY = "attorney"
    OTHER = "other"


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"


class DealStatus(str, enum.Enum):
    ACTIVE = "active"
    PENDING = "pending"
    UNDER_CONTRACT = "under_contract"
    CLOSED = "closed"
    EXPIRED = "expired"


class DealType(str, enum.Enum):
    PROPERTY_FOR_SALE = "property_for_sale"
    PROPERTY_WANTED = "property_wanted"
    JOINT_VENTURE = "joint_venture"
    FUNDING_NEEDED = "funding_needed"
    SERVICE_OFFERED = "service_offered"
    SERVICE_NEEDED = "service_needed"
    OTHER = "other"


class ConnectionStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"


class MessageStatus(str, enum.Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"


# ─── Users Table ──────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)  # UUID
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    headline = Column(String(255), nullable=True)  # e.g. "Residential Agent | Miami"
    bio = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    company_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.AGENT)
    subscription_tier = Column(
        Enum(SubscriptionTier), nullable=False, default=SubscriptionTier.FREE
    )
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    locations = relationship("UserLocation", back_populates="user", cascade="all, delete-orphan")
    sent_connections = relationship("Connection", foreign_keys="Connection.requester_id",
                                    back_populates="requester", cascade="all, delete-orphan")
    received_connections = relationship("Connection", foreign_keys="Connection.addressee_id",
                                        back_populates="addressee", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id",
                                 back_populates="sender", cascade="all, delete-orphan")
    received_messages = relationship("Message", foreign_keys="Message.recipient_id",
                                     back_populates="recipient", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="creator", cascade="all, delete-orphan")
    deal_interactions = relationship("DealInteraction", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.id}: {self.full_name} ({self.role.value})>"


# ─── Locations ────────────────────────────────────────────────────────────────
class State(Base):
    """US States reference table."""
    __tablename__ = "states"

    code = Column(String(2), primary_key=True)  # e.g. "FL"
    name = Column(String(100), nullable=False, unique=True)

    cities = relationship("City", back_populates="state", cascade="all, delete-orphan")


class City(Base):
    """Cities within states."""
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    state_code = Column(String(2), ForeignKey("states.code"), nullable=False)
    slug = Column(String(200), nullable=False)  # e.g. "miami-fl"

    state = relationship("State", back_populates="cities")
    zip_codes = relationship("ZipCode", back_populates="city", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("name", "state_code", name="uq_city_state"),
        Index("ix_cities_slug", "slug"),
    )


class ZipCode(Base):
    """ZIP codes within cities."""
    __tablename__ = "zip_codes"

    code = Column(String(10), primary_key=True)  # e.g. "33101"
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    city = relationship("City", back_populates="zip_codes")
    user_locations = relationship("UserLocation", back_populates="zip_code_rel", cascade="all, delete-orphan")


class UserLocation(Base):
    """Maps users to the locations they serve."""
    __tablename__ = "user_locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    zip_code = Column(String(10), ForeignKey("zip_codes.code"), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="locations")
    zip_code_rel = relationship("ZipCode", back_populates="user_locations")

    __table_args__ = (
        UniqueConstraint("user_id", "zip_code", name="uq_user_zip"),
        Index("ix_user_locations_zip", "zip_code"),
        Index("ix_user_locations_user", "user_id"),
    )


# ─── Connections / Network Graph ──────────────────────────────────────────────
class Connection(Base):
    """Connections between users (undirected, with requester/addressee semantics)."""
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    requester_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    addressee_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(ConnectionStatus), nullable=False, default=ConnectionStatus.PENDING)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    requester = relationship("User", foreign_keys=[requester_id], back_populates="sent_connections")
    addressee = relationship("User", foreign_keys=[addressee_id], back_populates="received_connections")

    __table_args__ = (
        UniqueConstraint("requester_id", "addressee_id", name="uq_connection_pair"),
        Index("ix_connections_requester", "requester_id"),
        Index("ix_connections_addressee", "addressee_id"),
        Index("ix_connections_status", "status"),
    )


# ─── Messages ─────────────────────────────────────────────────────────────────
class Message(Base):
    """Direct messages between connected users."""
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True)  # UUID
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    recipient_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    subject = Column(String(255), nullable=True)
    body = Column(Text, nullable=False)
    status = Column(Enum(MessageStatus), nullable=False, default=MessageStatus.SENT)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_messages")

    __table_args__ = (
        Index("ix_messages_sender", "sender_id"),
        Index("ix_messages_recipient", "recipient_id"),
        Index("ix_messages_created", "created_at"),
    )


# ─── Deal Listings (Marketplace) ─────────────────────────────────────────────-
class Deal(Base):
    """Deal/property listings in the marketplace."""
    __tablename__ = "deals"

    id = Column(String(36), primary_key=True)  # UUID
    creator_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    deal_type = Column(Enum(DealType), nullable=False)
    status = Column(Enum(DealStatus), nullable=False, default=DealStatus.ACTIVE)
    
    # Location
    state_code = Column(String(2), ForeignKey("states.code"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    zip_code = Column(String(10), ForeignKey("zip_codes.code"), nullable=True)
    address = Column(String(500), nullable=True)  # optional precise address
    
    # Deal details
    price = Column(Float, nullable=True)
    square_feet = Column(Integer, nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Float, nullable=True)
    property_type = Column(String(100), nullable=True)  # "single_family", "multi_family", "commercial", "land"
    
    # Metadata
    tags = Column(JSON, nullable=True)  # ["fixer-upper", "distressed", "off-market"]
    media_urls = Column(JSON, nullable=True)  # ["https://..."]
    views_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    creator = relationship("User", back_populates="deals")
    interactions = relationship("DealInteraction", back_populates="deal", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_deals_creator", "creator_id"),
        Index("ix_deals_type", "deal_type"),
        Index("ix_deals_status", "status"),
        Index("ix_deals_state", "state_code"),
        Index("ix_deals_zip", "zip_code"),
        Index("ix_deals_created", "created_at"),
        Index("ix_deals_price", "price"),
    )


class DealInteraction(Base):
    """Tracks user interactions with deals (saves, inquiries, shares)."""
    __tablename__ = "deal_interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    deal_id = Column(String(36), ForeignKey("deals.id"), nullable=False)
    interaction_type = Column(String(50), nullable=False)  # "save", "inquiry", "share", "view"
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="deal_interactions")
    deal = relationship("Deal", back_populates="interactions")

    __table_args__ = (
        Index("ix_deal_interactions_user", "user_id"),
        Index("ix_deal_interactions_deal", "deal_id"),
        Index("ix_deal_interactions_type", "interaction_type"),
    )


# ─── Helper: Create All Tables ────────────────────────────────────────────────
def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


def get_engine():
    return engine