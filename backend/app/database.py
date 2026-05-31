"""
Jumbos - Database Session Management
"""
from sqlalchemy.orm import sessionmaker, Session
from app.models import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency: yields a database session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from app.models import create_tables
    create_tables()