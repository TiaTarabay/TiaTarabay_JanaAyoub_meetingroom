"""
Rooms Service API Router
------------------------

This module contains all API endpoints related to managing meeting rooms.
It supports both public read operations and restricted administrative
operations such as creating, updating, and deleting rooms.

Roles:
    - Admin: Full access (create/update/delete rooms)
    - Facility Manager: Has the same permissions as admin for room management
    - Regular User / Moderator / Auditor: Read-only access

Endpoints:
    - GET /rooms/              → List all rooms (public)
    - GET /rooms/{id}          → Get a single room (public)
    - POST /rooms/             → Create a new room (admin/FM only)
    - PUT /rooms/{id}          → Update an existing room (admin/FM only)
    - DELETE /rooms/{id}       → Delete a room (admin/FM only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .models import Room
from .schemas import RoomCreate, RoomUpdate, RoomRead
from common.db.connection import get_db
from common.auth.auth_backend import get_current_user
from users_service.models import User   # required for RBAC
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

# Authentication Wrapper

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def CurrentUser(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Retrieve the currently authenticated user based on the JWT access token.

    Args:
        token (str): Bearer token provided in the Authorization header.
        db (Session): Database session dependency.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If authentication fails.
    """
    return get_current_user(token=token, db=db, user_model=User)


def require_admin(user: User):
    """
    Ensure that the current user has admin privileges.

    Args:
        user (User): The authenticated user.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )

# PUBLIC ENDPOINTS (Accessible by all roles)

@router.get("/", response_model=list[RoomRead])
def get_all_rooms(db: Session = Depends(get_db)):
    """
    Retrieve a list of all rooms in the system.

    Returns:
        list[RoomRead]: All stored room records.
    """
    return db.query(Room).all()


@router.get("/{room_id}", response_model=RoomRead)
def get_room(room_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single room by its ID.

    Args:
        room_id (int): The ID of the room to retrieve.

    Returns:
        RoomRead: The room data if found.

    Raises:
        HTTPException: If the room does not exist.
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Room not found")
    return room


# ADMIN / FACILITY MANAGER ENDPOINTS
@router.post("/", response_model=RoomRead)
def create_room(
    payload: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    """
    Create a new meeting room.

    Only administrators and facility managers are allowed to perform this action.

    Args:
        payload (RoomCreate): The details of the room to be created.
        db (Session): Database session.
        current_user (User): Authenticated user performing the request.

    Returns:
        RoomRead: The created room.

    Raises:
        HTTPException: If a room with the same name already exists.
    """
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
    """
    Update information for an existing room.

    This includes modifying capacity, equipment, location, or availability.
    Only administrators and facility managers can update rooms.

    Args:
        room_id (int): ID of the room to update.
        payload (RoomUpdate): Fields to update.
        db (Session): Database session.
        current_user (User): Authenticated user.

    Returns:
        RoomRead: The updated room.

    Raises:
        HTTPException: If the room does not exist.
    """
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
    if payload.available is not None:
        room.available = payload.available

    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=204)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(CurrentUser),
):
    """
    Delete a room from the system.

    Only administrators and facility managers are permitted to delete rooms.

    Args:
        room_id (int): ID of the room to delete.
        db (Session): Database session.
        current_user (User): Authenticated user.

    Raises:
        HTTPException: If the room does not exist.
    """
    require_admin(current_user)

    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Room not found")

    db.delete(room)
    db.commit()
    return
