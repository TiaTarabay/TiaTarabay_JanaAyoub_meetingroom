"""
Users Service Main Application
------------------------------
This module initializes the FastAPI application for the Users Service.
It loads the database models, sets up the required tables, and attaches
all user-related API routes under the `/users` prefix.
"""

from fastapi import FastAPI
from .routers import router
from common.db.connection import Base, engine
from common.exceptions import add_exception_handlers

# Initialize the FastAPI application for the Users Service
app = FastAPI(title="Users Service")

# Add global exception handling
add_exception_handlers(app)

# Create database tables if they do not already exist
Base.metadata.create_all(bind=engine)

# API Versioning
app.include_router(router, prefix="/v1/users")

# Optional legacy path
app.include_router(router, prefix="/users")
