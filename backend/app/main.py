"""
Jumbos - Main FastAPI Application
A location-first real estate networking platform.
"""
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import auth, locations, users, connections, messages, deals, subscription


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(
    title="Jumbos API",
    description=(
        "A location-first real estate networking platform. "
        "Professionals connect by state, city, and ZIP code — "
        "find the right people in the right markets, fast."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ─── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Root ──────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "Jumbos API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# ─── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(locations.router)
app.include_router(users.router)
app.include_router(connections.router)
app.include_router(messages.router)
app.include_router(deals.router)
app.include_router(subscription.router)


# ─── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)