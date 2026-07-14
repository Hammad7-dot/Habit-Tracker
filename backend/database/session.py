"""
SQLAlchemy engine + session factory.
Works transparently with SQLite (dev) and PostgreSQL (production) based on
the DATABASE_URL in config.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # Needed only for SQLite to allow usage across threads (FastAPI's threadpool)
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
