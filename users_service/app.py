"""
Users Service Main Application

This module initializes the FastAPI application for the Users Service.
It loads the database models, sets up the required tables, and attaches
all user-related API routes under the `/users` prefix.

The Users Service is responsible for:
    - Registering new users
    - Authenticating users through JWT-based login
    - Managing personal profiles (update / delete)
    - Handling administrative actions (creating users, updating roles, deleting users)
    - Providing user information to other microservices

The service interacts with the shared database defined in
`common/db/connection.py`, and ensures that the `users` table exists
when the application starts.
"""

from fastapi import FastAPI
from .routers import router
from common.db.connection import Base, engine

# Initialize the FastAPI application for the Users Service
app = FastAPI(title="Users Service")

# Create database tables if they do not already exist
Base.metadata.create_all(bind=engine)

# Register the Users API routes under the "/users" URL prefix
app.include_router(router, prefix="/users")
