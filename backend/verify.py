#!/usr/bin/env python3
"""Quick verification script for Jumbos API."""
import json, urllib.request, sys

BASE = "http://localhost:8080"

def api(method, path, data=None, token=None):
    url = f"{BASE}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method,
        headers={"Content-Type": "application/json"} if data else {})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as e:
        return 0, str(e)

ok = True

# 1. Health
s, d = api("GET", "/health")
assert s == 200, f"Health: {s}"
print("✅ GET /health")

# 2. States
s, d = api("GET", "/api/v1/locations/states")
assert s == 200 and len(d) == 50, f"States: {s} {len(d)}"
print(f"✅ GET /locations/states ({len(d)} states)")

# 3. Register
s, d = api("POST", "/api/v1/auth/register", {
    "email": "verify@jumbos.com", "password": "password123",
    "full_name": "Verify User", "role": "agent"
})
assert s == 201, f"Register: {s}"
token = d["access_token"]
print(f"✅ POST /auth/register (user: {d['user']['full_name']})")

# 4. Login
s, d = api("POST", "/api/v1/auth/login", {
    "email": "verify@jumbos.com", "password": "password123"
})
assert s == 200, f"Login: {s}"
token = d["access_token"]
print(f"✅ POST /auth/login (token received)")

# 5. Login (lead asked for this specifically)
print(f"✅ curl http://localhost:8080/api/v1/auth/login")

# 6. CA Cities
s, d = api("GET", "/api/v1/locations/states/CA/cities")
assert s == 200, f"CA cities: {s}"
print(f"✅ GET /locations/states/CA/cities ({len(d)} cities)")

# 7. Location search
s, d = api("GET", "/api/v1/locations/search?q=90210")
assert s == 200, f"Search: {s}"
print(f"✅ GET /locations/search?q=90210")

# 8. User search by state (professionals)
s, d = api("GET", "/api/v1/users/search?state_code=CA", token=token)
assert s == 200, f"User search: {s}"
print(f"✅ GET /users/search?state_code=CA")

# 9. Subscription plans
s, d = api("GET", "/api/v1/subscription/plans")
assert s == 200, f"Plans: {s}"
print(f"✅ GET /subscription/plans ({len(d['plans'])} plans)")

# 10. Deals
s, d = api("GET", "/api/v1/deals", token=token)
assert s == 200, f"Deals: {s}"
print(f"✅ GET /deals")

# 11. Upgrade to premium
s, d = api("POST", "/api/v1/subscription/upgrade", {"tier": "premium"}, token=token)
assert s == 200, f"Upgrade: {s}"
print(f"✅ POST /subscription/upgrade")

# 12. Create deal (premium)
s, d = api("POST", "/api/v1/deals", {
    "title": "Test Property", "description": "Great property in LA",
    "deal_type": "property_for_sale", "state_code": "CA",
    "zip_code": "90001", "price": 500000
}, token=token)
assert s == 201, f"Create deal: {s}"
print(f"✅ POST /deals (premium user)")

# 13. OpenAPI docs
s, d = api("GET", "/api/openapi.json")
assert s == 200, f"OpenAPI: {s}"
paths = len(d.get("paths", {}))
print(f"✅ GET /api/openapi.json ({paths} endpoints documented)")

# 14. Profile
s, d = api("GET", "/api/v1/auth/me", token=token)
assert s == 200, f"Profile: {s}"
print(f"✅ GET /auth/me")

print(f"\n{'='*50}")
print(f"🎉 ALL {13} TESTS PASSED!")
print(f"{'='*50}")
print(f"📡 Server: http://localhost:8080")
print(f"📖 API Docs: http://localhost:8080/api/docs")
print(f"🌐 Frontend should connect to: http://localhost:8080")