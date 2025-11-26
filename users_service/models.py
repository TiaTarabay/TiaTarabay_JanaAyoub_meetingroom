"""
User Model

This module defines the SQLAlchemy model for the ``users`` table, which stores
all registered users in the Smart Meeting Room Management System. Users may
have different system roles, which determine the actions they are allowed to
perform (e.g., regular user, admin, facility manager, moderator, auditor).

The Users Service handles:
    - User registration and login
    - Password hashing and verification
    - Role-based authorization (RBAC)

Each user record contains login credentials, contact information, and a role
that defines their permissions across the different microservices.
"""

from sqlalchemy import Column, Integer, String
from common.db.connection import Base


class User(Base):
    """
    SQLAlchemy model representing a system user.

    Attributes:
        id (int): Primary key identifier for the user.
        username (str): Unique username used for logging in.
        email (str): Unique email address for the user.
        hashed_password (str): Securely hashed version of the user's password.
                               Stored using bcrypt or a similar hashing algorithm.
        role (str): The user's role in the system. Controls access permissions.

                     Examples:
                        - "regular_user"     (default)
                        - "admin"            (full user + room management)
                        - "facility_manager" (room management only)
                        - "moderator"        (review moderation)
                        - "auditor"          (read-only access)
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Role used for authorization checks throughout the system
    role = Column(String, default="regular_user", nullable=False)
