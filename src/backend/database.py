"""
SQLAlchemy engine + session factory.

Reads DATABASE_URL from the environment (or .env file).
Falls back to a local SQLite database when no value is set,
so the backend can run without PostgreSQL for development/demo.
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "sqlite:///./mission_readiness.db"
)

# SQLite needs check_same_thread=False; ignored for other engines.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
