from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .models import Room
from .schemas import RoomCreate, RoomUpdate, RoomRead
from common.db.connection import get_db
from common.auth.auth_backend import get_current_user
from users_service.models import User   # required for RBAC
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

# --------------------------------------
# FIXED AUTH: Correct CurrentUser wrapper
# --------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def CurrentUser(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    # Pass token + db + User model to shared get_current_user
    return get_current_user(token=token, db=db, user_model=User)


# RBAC checks
def require_admin(user: User):
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )


# ============================
#       PUBLIC ENDPOINTS
# ============================

@router.get("/", response_model=list[RoomRead])
def get_all_rooms(db: Session = Depends(get_db)):
    return db.query(Room).all()


@router.get("/{room_id}", response_model=RoomRead)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Room not found")
    return room


# ============================
#     ADMIN-ONLY ENDPOINTS
# ============================

@router.post("/", response_model=RoomRead)
def create_room(
    payload: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    require_admin(current_user)

    existing = db.query(Room).filter(Room.name == payload.name).first()
    if existing:
        raise HTTPException(400, "Room already exists")

    room = Room(
        name=payload.name,
        capacity=payload.capacity,
        equipment=payload.equipment,
        location=payload.location,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.put("/{room_id}", response_model=RoomRead)
def update_room(
    room_id: int,
    payload: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    require_admin(current_user)

    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Room not found")

    if payload.name is not None:
        room.name = payload.name
    if payload.capacity is not None:
        room.capacity = payload.capacity
    if payload.equipment is not None:
        room.equipment = payload.equipment
    if payload.location is not None:
        room.location = payload.location


    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=204)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    require_admin(current_user)

    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Room not found")

    db.delete(room)
    db.commit()
    return
