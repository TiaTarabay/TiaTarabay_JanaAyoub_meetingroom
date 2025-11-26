"""
Rooms Service Main Application

This module initializes the FastAPI application for the Rooms Service.
It sets up the database tables, loads the API router, and exposes all
room-related endpoints under the `/rooms` prefix.

The Rooms Service is responsible for:
- Creating, updating, and deleting meeting rooms (admin + facility manager)
- Retrieving room details (all roles)
- Managing room availability (marking rooms out-of-service)

This service communicates with the shared database defined in `common/db/connection.py`.
"""

from fastapi import FastAPI
from .routers import router
from common.db.connection import Base, engine

app = FastAPI(title="Rooms Service")

# Create database tables if they do not exist.
# This ensures the `rooms` table is available when the service starts.
Base.metadata.create_all(bind=engine)

# Include the Rooms API router under the `/rooms` path.
app.include_router(router, prefix="/rooms")
