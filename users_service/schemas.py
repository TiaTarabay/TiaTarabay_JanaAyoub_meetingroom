"""
Pydantic Schemas for the Users Service
--------------------------------------

This module defines all Pydantic models used for validating input and output
data in the Users Service. These schemas ensure that user registration,
authentication, profile updates, and administrative actions follow a clear and
consistent data structure.

Schemas included:
    - UserBase
    - UserLogin
    - UserCreate
    - AdminCreateUser
    - UserUpdate
    - RoleUpdate
    - UserRead
"""

from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    """
    Base schema containing the common fields used across user operations.

    Fields:
        username (str): Unique username chosen by the user.
        email (str): Unique email address associated with the account.
    """
    username: str
    email: str


class UserLogin(BaseModel):
    """
    Schema used when a user attempts to log in.

    Required by:
        POST /users/login

    Fields:
        username (str): Username of the account.
        password (str): Plaintext password provided during login.
    """
    username: str
    password: str


class UserCreate(UserBase):
    """
    Public registration schema for creating a new user account.

    Used by:
        POST /users/register

    Fields:
        username (str): New user's username.
        email (str): New user's email.
        password (str): Plaintext password (will be hashed before storage).
    """
    password: str


class AdminCreateUser(UserBase):
    """
    Schema used by administrators to create users with a specific role.

    Used by:
        POST /users/admin/users

    Fields:
        username (str): Username of the new account.
        email (str): Email of the new account.
        password (str): Plaintext password for the account.
        role (str): Role assigned to the user (e.g., "admin", "auditor").
    """
    password: str
    role: str


class UserUpdate(BaseModel):
    """
    Schema for updating an existing user's profile.

    Used by:
        PUT /users/update/{user_id}
        PUT /users/admin/users/{user_id}

    Notes:
        All fields are optional to allow partial updates.

    Fields:
        username (str | None): New username.
        email (str | None): New email address.
        password (str | None): New password (hashed before storage).
    """
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class RoleUpdate(BaseModel):
    """
    Schema for updating a user's role.

    Used by:
        PATCH /users/admin/users/{user_id}/role

    Fields:
        role (str): New role value to assign.
    """
    role: str


class UserRead(BaseModel):
    """
    Schema returned when sending user information back to the client.

    Used by:
        GET /users/me
        GET /users/users
        GET /users/username/{username}
        POST /users/register
        POST /users/admin/users

    Fields:
        id (int): Unique user ID.
        username (str): Username associated with the account.
        email (str): Email associated with the account.
        role (str): User's role (determines access permissions).

    Config:
        from_attributes = True
            Allows conversion from SQLAlchemy ORM models to Pydantic models.
    """
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True
