#!/usr/bin/env python3
"""Full stability test - run after server restart"""
import urllib.request, urllib.error, json, sys, time

BASE = "http://localhost:8000"

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
        body = e.read()
        try:
            return e.code, json.loads(body)
        except:
            return e.code, {"raw": body.decode()[:200]}
    except Exception as e:
        return 0, {"error": str(e)}

passed = 0
failed = 0

def t(name):
    global passed, failed
    print(f"  {'✅' if name[0] else '❌'} {name[1]} (status={name[2]})")
    if name[0]:
        passed += 1
    else:
        failed += 1

print("=== STABILITY TEST ===\n")

# 1. Basic
s, d = api("GET", "/health")
t((s==200 and d.get("status")=="ok", "GET /health", s))

# 2. States
s, d = api("GET", "/api/v1/locations/states")
t((s==200 and len(d)==50, "GET /locations/states (50)", s))

# 3. Cities
s, d = api("GET", "/api/v1/locations/states/FL/cities")
t((s==200, "GET /locations/states/FL/cities", s))

# 4. Search
s, d = api("GET", "/api/v1/locations/search?q=miami")
t((s==200 and len(d.get("cities",[]))>0, "GET /locations/search?q=miami", s))

# 5. Plans
s, d = api("GET", "/api/v1/subscription/plans")
t((s==200, "GET /subscription/plans", s))

# 6. Register
s, d = api("POST", "/api/v1/auth/register", {
    "email": "stability@test.com", "password": "password123",
    "full_name": "Stability User", "role": "agent"
})
token = d.get("access_token", "")
t((s==201 and bool(token), "POST /auth/register (201 + token)", s))

# 7. Login with fresh credentials
s, d = api("POST", "/api/v1/auth/login", {
    "email": "stability@test.com", "password": "password123"
})
token = d.get("access_token", "")
t((s==200 and bool(token), "POST /auth/login (200 + token)", s))

# 8. Profile
s, d = api("GET", "/api/v1/auth/me", token=token)
t((s==200, "GET /auth/me", s))

# 9. User search
s, d = api("GET", "/api/v1/users/search?state_code=FL", token=token)
t((s==200, "GET /users/search?state_code=FL", s))

# 10. Add location
s, d = api("POST", "/api/v1/locations/me", {"zip_code": "33101", "is_primary": True}, token=token)
t((s==201, "POST /locations/me", s))

# 11. Get locations
s, d = api("GET", "/api/v1/locations/me", token=token)
t((s==200, "GET /locations/me", s))

# 12. Upgrade to premium
s, d = api("POST", "/api/v1/subscription/upgrade", {"tier": "premium"}, token=token)
tier = d.get("subscription_tier", "") if isinstance(d, dict) else ""
t((s==200 and tier=="premium", "POST /subscription/upgrade (premium)", s))

# 13. Create deal (requires premium) - use trailing slash
s, d = api("POST", "/api/v1/deals/", {
    "title": "Miami Property", "description": "Beautiful 3BR/2BA",
    "deal_type": "property_for_sale", "state_code": "FL",
    "zip_code": "33101", "price": 450000
}, token=token)
deal_id = d.get("id", "") if isinstance(d, dict) else ""
t((s==201 and bool(deal_id), "POST /deals (premium, 201)", s))

# 14. Browse deals
s, d = api("GET", "/api/v1/deals/?state_code=FL", token=token)
total = d.get("total", 0) if isinstance(d, dict) else 0
t((s==200 and total>0, "GET /deals?state_code=FL", s))

# 15. Get specific deal
s, d = api("GET", f"/api/v1/deals/{deal_id}", token=token)
t((s==200, "GET /deals/{id}", s))

# 16. Register second user
s2, d2 = api("POST", "/api/v1/auth/register", {
    "email": "alice@test.com", "password": "password123",
    "full_name": "Alice", "role": "investor"
})
token2 = d2.get("access_token", "") if s2==201 else ""
alice_id = d2.get("user", {}).get("id", "") if isinstance(d2, dict) else ""

# 17. Request connection
s, d = api("POST", "/api/v1/connections/request", {"addressee_id": alice_id}, token=token)
t((s==201, "POST /connections/request", s))
conn_id = d.get("id", 0) if isinstance(d, dict) else 0

# Accept connection (as alice)
if conn_id:
    api("POST", f"/api/v1/connections/{conn_id}/accept", token=token2)

# 18. Send message (premium user)
s, d = api("POST", "/api/v1/messages/send", {
    "recipient_id": alice_id, "subject": "Hi!", "body": "Let's connect"
}, token=token)
t((s==201, "POST /messages/send (premium)", s))

# 19. Unread count
s, d = api("GET", "/api/v1/messages/unread/count", token=token2)
t((s==200, "GET /messages/unread/count", s))

# 20. OpenAPI
s, d = api("GET", "/api/openapi.json")
paths = len(d.get("paths", {})) if isinstance(d, dict) else 0
t((s==200 and paths>=20, f"GET /api/openapi.json ({paths} endpoints)", s))

# Summary
print(f"\n{'='*50}")
print(f"RESULTS: {passed} passed, {failed} failed")
print(f"{'='*50}")
sys.exit(0 if failed==0 else 1)
