"""
Pydantic Schemas for the Rooms Service

This module defines the data validation schemas used by the Rooms Service.
These schemas ensure that incoming requests contain valid data and that
responses returned to clients follow a consistent structure.

Schemas included:
    - RoomCreate : Used when creating a new room.
    - RoomUpdate : Used when partially updating an existing room.
    - RoomRead   : Used when returning room information to the client.
"""

from pydantic import BaseModel
from typing import Optional


class RoomCreate(BaseModel):
    """
    Schema for creating a new meeting room.

    Required by:
        POST /rooms/

    Fields:
        name (str): Unique name of the room.
        capacity (int): Maximum number of occupants.
        equipment (str): Comma-separated list of available equipment.
        location (str): Physical location (building, floor, room number).
        available (bool): Whether the room is available for booking.
                          Defaults to True.
    """
    name: str
    capacity: int
    equipment: str
    location: str
    available: bool = True


class RoomUpdate(BaseModel):
    """
    Schema for updating an existing room.

    Used by:
        PUT /rooms/{room_id}

    All fields are optional to allow partial updates.
    Only fields provided by the client will be modified.

    Fields:
        name (str | None): New room name.
        capacity (int | None): Updated seating capacity.
        equipment (str | None): Updated equipment list.
        location (str | None): Updated room location.
        available (bool | None): Availability flag (True/False).
    """
    name: Optional[str] = None
    capacity: Optional[int] = None
    equipment: Optional[str] = None
    location: Optional[str] = None
    available: Optional[bool] = None


class RoomRead(BaseModel):
    """
    Schema returned when sending room information to the client.

    Used by:
        GET /rooms/
        GET /rooms/{room_id}
        POST /rooms/
        PUT /rooms/{room_id}

    Fields:
        id (int): Unique identifier of the room.
        name (str): Name of the room.
        capacity (int): Seating capacity.
        equipment (str): Equipment list.
        location (str): Physical location of the room.
        available (bool): Whether the room is currently available.
    """
    id: int
    name: str
    capacity: int
    equipment: str
    location: str
    available: bool

    # Required for converting SQLAlchemy ORM objects into Pydantic models.
    model_config = {
        "from_attributes": True
    }
