"""One-shot: seed, start server, test, report. Run from /home/agent-backend-engineer/jumbos-backend"""
import os, sys, time, subprocess, json, urllib.request, urllib.error

os.chdir("/home/agent-backend-engineer/jumbos-backend")
PORT = 8000
BASE = f"http://localhost:{PORT}"

# 1. Kill old servers
print("=== Killing old servers ===")
subprocess.run("pkill -9 -f uvicorn", shell=True, stderr=subprocess.DEVNULL)
subprocess.run("fuser -k 8000/tcp 2>/dev/null; fuser -k 8080/tcp 2>/dev/null", shell=True)
time.sleep(2)

# 2. Delete old DB and re-seed
print("=== Re-seeding database ===")
os.makedirs("app", exist_ok=True)
if os.path.exists("jumbos.db"):
    os.remove("jumbos.db")
    print("Deleted old jumbos.db")

from app.models import create_tables
create_tables()
from seed import seed
seed()
print("Database seeded successfully")

# 3. Start server
print(f"=== Starting server on port {PORT} ===")
srv = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(PORT)],
    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
)
time.sleep(4)

# Check if server is running
if srv.poll() is not None:
    _, stderr = srv.communicate()
    print(f"SERVER FAILED: {stderr.decode()[:500]}")
    sys.exit(1)

print(f"Server PID={srv.pid} running on {BASE}")

# 4. API helper
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
        return 0, str(e)[:200]

# 5. Run tests
print("\n=== RUNNING TESTS ===")
passed = 0
failed = 0

def test(name, status_ok, condition=True):
    global passed, failed
    status_str = f"[{'PASS' if condition else 'FAIL'}] {name} (status={status_ok})"
    print(f"  {'✅' if condition else '❌'} {name}")
    if condition:
        passed += 1
    else:
        failed += 1

# Root & health
s, d = api("GET", "/")
test("GET /", s, s == 200)
s, d = api("GET", "/health")
test("GET /health", s, s == 200 and d.get("status") == "ok")

# States
s, d = api("GET", "/api/v1/locations/states")
test("GET /locations/states", s, s == 200 and len(d) == 50)

# FL cities
s, d = api("GET", "/api/v1/locations/states/FL/cities")
test("GET /locations/states/FL/cities", s, s == 200 and len(d) >= 1)

# CA cities
s, d = api("GET", "/api/v1/locations/states/CA/cities")
test("GET /locations/states/CA/cities", s, s == 200 and len(d) >= 1)

# Location search
s, d = api("GET", "/api/v1/locations/search?q=miami")
test("GET /locations/search?q=miami", s, s == 200)

# ZIP code search
s, d = api("GET", "/api/v1/locations/search?q=90210")
test("GET /locations/search?q=90210", s, s == 200)

# Plans
s, d = api("GET", "/api/v1/subscription/plans")
test("GET /subscription/plans", s, s == 200 and len(d.get("plans", [])) == 2)

# Register
s, d = api("POST", "/api/v1/auth/register", {
    "email": "demo@jumbos.com", "password": "securepassword123",
    "full_name": "Demo User", "role": "agent"
})
token = d.get("access_token", "") if s == 201 else ""
test("POST /auth/register (demo)", s, s == 201 and token != "")

# Login
s, d = api("POST", "/api/v1/auth/login", {
    "email": "demo@jumbos.com", "password": "securepassword123"
})
token = d.get("access_token", "") if s == 200 else ""
test("POST /auth/login", s, s == 200 and token != "")

# Profile
s, d = api("GET", "/api/v1/auth/me", token=token)
test("GET /auth/me", s, s == 200 and d.get("email") == "demo@jumbos.com")

# User search
s, d = api("GET", "/api/v1/users/search?state_code=FL", token=token)
test("GET /users/search?state_code=FL", s, s == 200)

# Add location
s, d = api("POST", "/api/v1/locations/me", {"zip_code": "33101", "is_primary": True}, token=token)
test("POST /locations/me (add zip)", s, s == 201)

# Get locations
s, d = api("GET", "/api/v1/locations/me", token=token)
test("GET /locations/me", s, s == 200)

# Upgrade to premium
s, d = api("POST", "/api/v1/subscription/upgrade", {"tier": "premium"}, token=token)
test("POST /subscription/upgrade", s, s == 200 and d.get("subscription_tier") == "premium")

# Create deal (premium)
s, d = api("POST", "/api/v1/deals", {
    "title": "Miami Beach Property",
    "description": "Beautiful 3BR/2BA near the beach",
    "deal_type": "property_for_sale", "state_code": "FL",
    "zip_code": "33101", "price": 450000
}, token=token)
deal_id = d.get("id", "")
test("POST /deals (premium)", s, s == 201 and deal_id != "")

# Browse deals by location
s, d = api("GET", "/api/v1/deals?state_code=FL", token=token)
test("GET /deals?state_code=FL", s, s == 200)

# Get specific deal
s, d = api("GET", f"/api/v1/deals/{deal_id}", token=token)
test("GET /deals/{id}", s, s == 200)

# Register second user for connections/messages
s2, d2 = api("POST", "/api/v1/auth/register", {
    "email": "alice@jumbos.com", "password": "password123",
    "full_name": "Alice Agent", "role": "investor"
})
token2 = d2.get("access_token", "")
alice_id = d2.get("user", {}).get("id", "")

# Upgrade alice to premium too
api("POST", "/api/v1/subscription/upgrade", {"tier": "premium"}, token=token2)

# Request connection
s, d = api("POST", "/api/v1/connections/request", {"addressee_id": alice_id}, token=token)
test("POST /connections/request", s, s == 201)

# Send message (premium user can)
s, d = api("POST", "/api/v1/messages/send", {
    "recipient_id": alice_id, "subject": "Hello!", "body": "Hi Alice, interested in your property listing."
}, token=token)
test("POST /messages/send", s, s == 201)

# Unread count
s, d = api("GET", "/api/v1/messages/unread/count", token=token2)
test("GET /messages/unread/count", s, s == 200)

# OpenAPI docs
s, d = api("GET", "/api/openapi.json")
paths = len(d.get("paths", {})) if isinstance(d, dict) else 0
test(f"GET /api/openapi.json ({paths} endpoints)", s, s == 200 and paths >= 20)

# Summary
print(f"\n{'='*50}")
print(f"RESULTS: {passed} passed, {failed} failed")
print(f"{'='*50}")
if failed == 0:
    print("🎉 ALL TESTS PASSED!")
else:
    print(f"⚠️  {failed} test(s) failed")
print(f"\n📡 Server: {BASE}")
print(f"📖 Docs: {BASE}/api/docs")
print(f"\nDemo Login: POST {BASE}/api/v1/auth/login")
print(f'  {{"email":"demo@jumbos.com","password":"securepassword123"}}')

srv.terminate()
srv.wait(timeout=5)