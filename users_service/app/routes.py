from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .models import User
from .schemas import UserCreate, UserLogin, UserUpdate
from .db import get_db
from .auth import hash_password, verify_password

router = APIRouter()

@router.get("/test")
def test():
    return {"msg": "Users service  working"}

@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # this is to check if this username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = hash_password(user.password)

    new_user = User(
        name=user.name,
        username=user.username,
        email=user.email,
        password=hashed_pw,
        role="regular_user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"msg": "User registered successfully", "user_id": new_user.id}

@router.post("/login")
def login_user(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Wrong password")

    return {"msg": "Login successful", "user_id": user.id}

@router.put("/update/{user_id}")
def update_profile(user_id: int, info: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if info.name:
        user.name = info.name
    if info.email:
        user.email = info.email
    if info.password:
        user.password = hash_password(info.password)

    db.commit()
    return {"msg": "Profile updated "}

@router.get("/{user_id}/bookings")
def get_booking_history(user_id: int):
    # This will be replaced once Bookings service is connected
    return {"msg": "Booking history placeholder for user", "user_id": user_id}
