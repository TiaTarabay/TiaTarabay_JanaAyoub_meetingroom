"""
Users Service API Router

This module implements all user-related API endpoints for the Smart Meeting
Room Management System. It handles registration, login, profile management,
and administrative user operations such as role assignments and account deletion.

Role Overview
- Regular User:
    Can register, log in, update their own profile, delete their own account.
- Admin:
    Has full access to all user operations including creating users,
    modifying accounts, deleting users, and changing roles.
- Auditor:
    Can view users (read-only) but cannot modify anything.

Endpoints Overview
Public Endpoints:
    - POST /register           : Register a new account
    - POST /login              : Authenticate user and return JWT token

Authenticated User Endpoints:
    - GET  /me                 : Get personal profile
    - DELETE /me               : Delete own account
    - PUT /update/{user_id}    : Update own account (username/email/password)

Admin-Only Endpoints:
    - POST /admin/users                    : Create a user with a specific role
    - GET  /users                          : Get all users (admin/auditor)
    - GET  /users/username/{username}      : Get a user by username
    - PUT  /admin/users/{id}               : Update a user's profile
    - DELETE /admin/users/{id}             : Delete a user
    - PATCH /admin/users/{id}/role         : Update a user's role
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .models import User
from .schemas import (
    UserCreate,
    UserLogin,
    UserUpdate,
    AdminCreateUser,
    RoleUpdate,
    UserRead,
)

# Shared authentication utilities
from common.db.connection import get_db
from common.auth.auth_backend import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter()

# Authentication wrapper using OAuth2 bearer token
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def CurrentUser(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Retrieve the currently authenticated user.

    Args:
        token (str): JWT access token provided in the Authorization header.
        db (Session): Active database session.

    Returns:
        User: The authenticated user instance.

    Raises:
        HTTPException: If authentication fails or token is invalid.
    """
    return get_current_user(token=token, db=db, user_model=User)


# RBAC Helper Functions

def require_admin(current_user: User):
    """
    Ensure that the current user has admin privileges.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )


def require_admin_or_auditor(current_user: User):
    """
    Restrict access to admin or auditor users only.

    Raises:
        HTTPException: If the user is neither admin nor auditor.
    """
    if current_user.role not in ["admin", "auditor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )



# Utility Test Route
@router.get("/test")
def test():
    """Simple test endpoint to verify Users Service is running."""
    return {"msg": "Users service working"}



# Public Authentication APIs


@router.post("/register", response_model=UserRead)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with the role ``regular_user``.

    Args:
        payload (UserCreate): Contains username, email, and password.
        db (Session): Database session.

    Returns:
        UserRead: The newly created user.

    Raises:
        HTTPException: If username or email already exists.
    """
    existing_user = (
        db.query(User)
        .filter((User.username == payload.username) | (User.email == payload.email))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    hashed_pw = get_password_hash(payload.password)

    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_pw,
        role="regular_user",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT access token.

    Args:
        payload (UserLogin): Contains username and password.
        db (Session): Database session.

    Returns:
        dict: Access token, token type, user role, and user ID.

    Raises:
        HTTPException: If credentials are incorrect.
    """
    user = db.query(User).filter(User.username == payload.username).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    access_token = create_access_token({"id": user.id, "role": user.role})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
    }


# Regular User Profile Endpoints

@router.put("/update/{user_id}")
def update_profile(user_id: int, info: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user's profile.

    Regular users can only update their own data.

    Args:
        user_id (int): ID of the user to update.
        info (UserUpdate): Updated username/email/password.
        db (Session): Database session.

    Returns:
        dict: Confirmation message.

    Raises:
        HTTPException: If user does not exist.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if info.username:
        user.username = info.username
    if info.email:
        user.email = info.email
    if info.password:
        user.hashed_password = get_password_hash(info.password)

    db.commit()
    db.refresh(user)
    return {"msg": "Profile updated", "user_id": user.id}


@router.delete("/me", status_code=204)
def delete_own_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    """
    Delete the authenticated user's own account.

    Returns:
        None
    """
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return


@router.get("/me", response_model=UserRead)
def get_my_profile(current_user: User = Depends(CurrentUser)):
    """
    Retrieve the authenticated user's own profile.

    Returns:
        UserRead: Profile of the current user.
    """
    return current_user


# Booking History (Stub)

@router.get("/{user_id}/bookings")
def get_booking_history(user_id: int):
    """
    Placeholder endpoint for retrieving a user's booking history.

    (To be implemented in the Bookings Service.)

    Args:
        user_id (int): User whose booking history is requested.
    """
    return {"msg": "Booking history placeholder", "user_id": user_id}



# Admin-Only User Management

@router.post("/admin/users", response_model=UserRead)
def admin_create_user(
    payload: AdminCreateUser,
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    """
    Admin-only: Create a user with a specific role.

    Args:
        payload (AdminCreateUser): User info including role.
        db (Session): Database session.
        current_user (User): Authenticated admin.

    Returns:
        UserRead: Newly created user.

    Raises:
        HTTPException: If user already exists.
    """
    require_admin(current_user)

    existing_user = (
        db.query(User)
        .filter((User.username == payload.username) | (User.email == payload.email))
        .first()
    )

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = get_password_hash(payload.password)

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_pw,
        role=payload.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/users", response_model=list[UserRead])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    """
    Retrieve all users.

    Accessible by:
        - Admin
        - Auditor
    """
    require_admin_or_auditor(current_user)
    return db.query(User).all()


@router.get("/users/username/{username}", response_model=UserRead)
def get_user_by_username(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    """
    Retrieve a user by username.

    Accessible by:
        - Admin
        - Auditor

    Raises:
        HTTPException: If the user is not found.
    """
    require_admin_or_auditor(current_user)

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/admin/users/{user_id}", response_model=UserRead)
def admin_update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    """
    Admin-only: Update any user's profile.

    Args:
        user_id (int): ID of the user to update.
        payload (UserUpdate): New information.
    """
    require_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.username:
        user.username = payload.username
    if payload.email:
        user.email = payload.email
    if payload.password:
        user.hashed_password = get_password_hash(payload.password)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/admin/users/{user_id}", status_code=204)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    """
    Admin-only: Delete a user account.

    Args:
        user_id (int): ID of the user to delete.
    """
    require_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return


@router.patch("/admin/users/{user_id}/role", response_model=UserRead)
def admin_update_role(
    user_id: int,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    """
    Admin-only: Update a user's system role.

    Args:
        user_id (int): ID of the user whose role will be modified.
        payload (RoleUpdate): Contains the new role value.
    """
    require_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user
