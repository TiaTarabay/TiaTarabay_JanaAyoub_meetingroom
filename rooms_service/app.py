"""
Rooms Service Main Application

This module initializes the FastAPI application for the Rooms Service.
It sets up the database tables, loads the API router, and exposes all
room-related endpoints under the `/rooms` prefix.

The Rooms Service is responsible for:
- Creating, updating, and deleting meeting rooms
- Retrieving room details
- Managing room availability

This service communicates with the shared database defined in `common/db/connection.py`.
"""

from fastapi import FastAPI
from .routers import router
from common.db.connection import Base, engine
from common.exceptions import add_exception_handlers

# Initialize FastAPI app
app = FastAPI(title="Rooms Service")

# Add global exception handlers
add_exception_handlers(app)

# Create DB tables
Base.metadata.create_all(bind=engine)

# Versioned API routes
app.include_router(router, prefix="/v1/rooms")

# Optional legacy endpoint (backward compatibility)
app.include_router(router, prefix="/rooms")
