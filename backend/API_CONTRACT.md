# Jumbos API — Complete API Contract

## Overview

Welcome to the Jumbos API contract. Jumbos is a **location-first real estate networking platform**. Professionals connect by state, city, and ZIP code — find the right people in the right markets, fast.

**Base URL:** `http://localhost:8000`  
**API Docs (Swagger):** `/api/docs`  
**ReDoc:** `/api/redoc`  
**OpenAPI Spec:** `/api/openapi.json`

**Auth:** Bearer JWT token in `Authorization` header

---

## Authentication

All endpoints except `POST /api/v1/auth/register` and `POST /api/v1/auth/login` require authentication.

### Free Tier vs Premium

| Feature | Free | Premium |
|---|---|---|
| Browse network/profiles | ✅ | ✅ |
| View deal listings (read-only) | ✅ | ✅ |
| Receive connection requests | ✅ | ✅ |
| Receive messages | ✅ | ✅ |
| Send messages to connected users | ❌ | ✅ |
| Post deal listings | ❌ | ✅ |
| Interact with deals (save/inquiry) | ❌ | ✅ |
| Unlimited connections | ❌ | ✅ |
| Priority support | ❌ | ✅ |

---

## Endpoints

### 1. Authentication

#### POST /api/v1/auth/register
**Description:** Register a new user account  
**Auth:** None  
**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "Jane Doe",
  "role": "agent",
  "phone": "+13055551234",
  "company_name": "Doe Realty"
}
```
**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Jane Doe",
    "role": "agent",
    "subscription_tier": "free",
    ...
  }
}
```
**Roles:** agent, broker, investor, wholesaler, contractor, mortgage_broker, hard_money_lender, property_manager, title_company, inspector, insurance, attorney, other

#### POST /api/v1/auth/login
**Description:** Login with email/password  
**Auth:** None  
**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```
**Response (200):** Same as register

#### GET /api/v1/auth/me
**Description:** Get current user profile  
**Auth:** Required

#### PATCH /api/v1/auth/me
**Description:** Update profile  
**Auth:** Required

---

### 2. Locations (Core Feature)

#### GET /api/v1/locations/states
**Description:** List all US states

#### GET /api/v1/locations/states/{state_code}/cities
**Description:** List cities in a state (e.g., `FL`)

#### GET /api/v1/locations/cities/{city_id}/zipcodes
**Description:** List ZIP codes in a city

#### GET /api/v1/locations/zipcodes/{zip_code}
**Description:** Get ZIP code details

#### GET /api/v1/locations/search?q=miami
**Description:** Search locations by city name, state, or ZIP code

#### GET /api/v1/locations/me
**Description:** Get current user's served locations (ZIP codes)

#### POST /api/v1/locations/me
**Description:** Add a served location  
**Request:**
```json
{
  "zip_code": "33101",
  "is_primary": true
}
```

#### DELETE /api/v1/locations/me/{location_id}
**Description:** Remove a served location

---

### 3. Users / Network

#### GET /api/v1/users/search?q=jane&role=agent&state_code=FL&zip_code=33101
**Description:** **Core value prop** — search professionals by name, role, and location (state, city, or ZIP code)

| Param | Type | Description |
|---|---|---|
| q | string | Free-text name search |
| role | string | Filter by profession |
| state_code | string | 2-letter state code |
| city | string | City name |
| zip_code | string | ZIP code |
| page | int | Default 1 |
| per_page | int | Default 20, max 100 |

#### GET /api/v1/users/{user_id}
**Description:** Get a user's public profile

#### GET /api/v1/users/{user_id}/locations
**Description:** Get locations a user serves

---

### 4. Connections

#### GET /api/v1/connections/?status=accepted
**Description:** List connections (pending/accepted)

#### POST /api/v1/connections/request
**Description:** Send connection request  
**Request:** `{"addressee_id": "user-uuid"}`

#### POST /api/v1/connections/{connection_id}/accept
**Description:** Accept a pending request

#### DELETE /api/v1/connections/{connection_id}
**Description:** Remove/decline connection

---

### 5. Messages

#### GET /api/v1/messages/
**Description:** List all messages (sent & received)

#### GET /api/v1/messages/conversation/{other_user_id}
**Description:** Get conversation thread with another user

#### POST /api/v1/messages/send
**Description:** Send a direct message (premium required for sending)  
**Request:**
```json
{
  "recipient_id": "user-uuid",
  "subject": "Re: Miami Beach property",
  "body": "Hi, I'm interested in the deal you posted..."
}
```
**Note:** Both users must be connected (accepted connection).

#### PATCH /api/v1/messages/{message_id}/read
**Description:** Mark message as read

#### GET /api/v1/messages/unread/count
**Description:** Get unread count

---

### 6. Deals (Marketplace)

#### GET /api/v1/deals/
**Description:** Browse deal listings with location-first filtering

| Param | Type | Description |
|---|---|---|
| deal_type | string | property_for_sale, property_wanted, joint_venture, etc. |
| state_code | string | 2-letter state code |
| city_id | int | Filter by city |
| zip_code | string | Filter by ZIP code |
| status | string | active (default), pending, under_contract, closed, expired |
| min_price | float | Min price |
| max_price | float | Max price |
| property_type | string | single_family, multi_family, commercial, land |
| min_bedrooms | int | |
| q | string | Text search in title/description |
| page / per_page | | Pagination |

#### POST /api/v1/deals/
**Description:** Create a deal listing (premium required)  
**Request:**
```json
{
  "title": "Fixer-upper in Miami Beach",
  "description": "3BR/2BA single-family home...",
  "deal_type": "property_for_sale",
  "state_code": "FL",
  "zip_code": "33101",
  "price": 450000,
  "bedrooms": 3,
  "bathrooms": 2,
  "property_type": "single_family",
  "tags": ["fixer-upper", "off-market"]
}
```

#### GET /api/v1/deals/my
**Description:** List current user's deals

#### GET /api/v1/deals/{deal_id}
**Description:** Get deal details

#### PATCH /api/v1/deals/{deal_id}
**Description:** Update own deal

#### DELETE /api/v1/deals/{deal_id}
**Description:** Delete own deal

#### POST /api/v1/deals/{deal_id}/interact?interaction_type=save
**Description:** Save, inquire, or share a deal (premium required)  
**Types:** save, inquiry, share

#### GET /api/v1/deals/{deal_id}/interactions/count
**Description:** Get interaction counts (saves, inquiries, shares)

---

### 7. Subscription

#### GET /api/v1/subscription/
**Description:** Get current subscription details & features

#### GET /api/v1/subscription/plans
**Description:** List available plans (Free vs Premium at $19.99/mo)

#### POST /api/v1/subscription/upgrade
**Description:** Upgrade/downgrade tier  
**Request:** `{"tier": "premium"}`

---

## Database Schema

### Tables

1. **users** — User accounts with roles, subscription tier
2. **states** — US states reference (code + name)
3. **cities** — Cities within states (name + state_code + slug)
4. **zip_codes** — ZIP codes within cities (code + city_id + lat/lng)
5. **user_locations** — Maps users to ZIP codes they serve (many-to-many)
6. **connections** — Network graph (requester/addressee/pending/accepted)
7. **messages** — DMs between connected users
8. **deals** — Marketplace listings (type, location, price, property details)
9. **deal_interactions** — User interactions with deals (save/inquiry/share)

### Key Indexes
- users: email (unique)
- cities: name+state_code (unique), slug
- user_locations: user_id+zip_code (unique)
- connections: requester_id+addressee_id (unique)
- deals: state_code, zip_code, price, created_at — all indexed for location-first search

---

## Tech Stack
- **Framework:** FastAPI (Python)
- **Database:** SQLAlchemy ORM with SQLite (pluggable via DATABASE_URL)
- **Auth:** JWT (python-jose) + bcrypt hashing
- **Validation:** Pydantic v2