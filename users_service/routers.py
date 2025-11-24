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
# IMPORT SHARED AUTH (common/)
from common.db.connection import get_db
from common.auth.auth_backend import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter()


# Helper wrappers for shared get_current_user

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def CurrentUser(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    return get_current_user(token=token, db=db, user_model=User)



# RBAC helpers
def require_admin(current_user: User):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )


def require_admin_or_auditor(current_user: User):
    if current_user.role not in ["admin", "auditor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )


# Simple test route
@router.get("/test")
def test():
    return {"msg": "Users service working"}


# Public registration
@router.post("/register", response_model=UserRead)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):

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


# Login
@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
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


# Update profile
@router.put("/update/{user_id}")
def update_profile(user_id: int, info: UserUpdate, db: Session = Depends(get_db)):

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

# Regular user delete own account
@router.delete("/me", status_code=204)
def delete_own_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return


# Booking history placeholder
@router.get("/{user_id}/bookings")
def get_booking_history(user_id: int):
    return {"msg": "Booking history placeholder", "user_id": user_id}


# Admin: Create user
@router.post("/admin/users", response_model=UserRead)
def admin_create_user(
    payload: AdminCreateUser,
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
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


# Admin/Auditor: Get all users
@router.get("/users", response_model=list[UserRead])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    require_admin_or_auditor(current_user)
    return db.query(User).all()

@router.get("/users/username/{username}", response_model=UserRead)
def get_user_by_username(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    require_admin_or_auditor(current_user)

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# Admin: update user
@router.put("/admin/users/{user_id}", response_model=UserRead)
def admin_update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
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


# Admin delete user
@router.delete("/admin/users/{user_id}", status_code=204)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    require_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return


# Admin: Update role
@router.patch("/admin/users/{user_id}/role", response_model=UserRead)
def admin_update_role(
    user_id: int,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    require_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user


# Self profile
@router.get("/me", response_model=UserRead)
def get_my_profile(current_user: User = Depends(CurrentUser)):
    return current_user
