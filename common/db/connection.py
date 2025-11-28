"""
Database connection layer.

For local development (running the services directly with Python),
we use a local SQLite database file.

For Docker deployment, the DATABASE_URL environment variable is
set by docker-compose to point to the PostgreSQL container.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# If DATABASE_URL is set (e.g. by Docker), use it.
# Otherwise, fall back to a local SQLite file for easy testing.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smartmeetingroom.db")


if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
