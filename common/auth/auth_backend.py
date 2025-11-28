"""
Authentication & Security Utilities:
------------------------------------
This module provides all authentication-related helpers used across the
microservices in the Smart Meeting Room Management System. It implements
password hashing, password verification, JWT token creation, and token
decoding to identify the currently logged-in user.

Functions in this module are used by:
    - Users Service (login, register, update profile, admin actions)
    - Rooms Service (role validation)
    - Bookings Service (ownership checks)
    - Reviews Service (user authentication)

Main Features:
- Secure password hashing using bcrypt (via passlib)
- JWT-based authentication
- Access token creation with expiration
- Token decoding to retrieve the authenticated user
- Integration with FastAPI OAuth2 bearer authentication
"""

from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext


# JWT Configuration

SECRET_KEY = "your_secret_key"   # Replace in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Token extractor for FastAPI (Authorization: Bearer <token>)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# Password Hashing Utilities

# bcrypt configuration for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password (str): The plaintext password.

    Returns:
        str: A securely hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.

    Args:
        plain_password (str): User-entered password.
        hashed_password (str): Password stored in the database.

    Returns:
        bool: True if the password is correct, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)



# JWT Token Creation

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token containing the user data (typically user ID + role).

    Args:
        data (dict): Payload to include in the JWT.
        expires_delta (timedelta | None): Optional custom expiration time.

    Returns:
        str: Encoded JWT token as a string.
    """
    payload = data.copy()

    # Token expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload["exp"] = expire

    # Encode token using SECRET_KEY
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


# Current User Retrieval (JWT Decoding)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db=None,
    user_model=None,
):
    """
    Decode the JWT token and retrieve the authenticated user from the database.

    This function is injected into FastAPI endpoints using Depends() to enforce
    authentication and identify the user making the request.

    Args:
        token (str): Extracted JWT token from Authorization header.
        db (Session): Database session used to query the user model.
        user_model (SQLAlchemy model): The User model class to query.

    Returns:
        user_model: The authenticated user object.

    Raises:
        RuntimeError: If db or user_model dependencies are missing.
        HTTPException: If token is invalid, expired, or user does not exist.
    """
    if db is None or user_model is None:
        raise RuntimeError("get_current_user() requires db and user_model arguments")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
        )

    # Fetch user from DB
    user = db.query(user_model).filter(user_model.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
