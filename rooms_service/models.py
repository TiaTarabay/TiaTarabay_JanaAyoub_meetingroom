"""
Room Model
-----------

This module defines the SQLAlchemy model for meeting rooms in the Smart
Meeting Room Management System. Each room entry stores general room
information (name, capacity, equipment, location) as well as its availability
status, which determines whether the room can be booked.

Fields:
    id (int): Primary key identifier for the room.
    name (str): Unique room name chosen by administrators (e.g., "Conference Room A").
    capacity (int): Maximum number of people the room can hold.
    equipment (str): Comma-separated list of available equipment
                     (e.g., "Projector, Whiteboard, HDMI").
    location (str): Physical location of the room (building, floor, room number).
    available (bool): Indicates whether the room is available for booking.
                      If set to False, the room is considered out-of-service.

This model is used by the Rooms Service to support all room-related CRUD
operations performed by administrators and facility managers.
"""

from sqlalchemy import Column, Integer, String, Boolean
from common.db.connection import Base


class Room(Base):
    """
    SQLAlchemy model representing a meeting room.

    This table stores the essential information needed to manage rooms in
    the system. A room can be created, updated, deleted, or marked as
    out-of-service by authorized roles (admin and facility manager).

    Attributes:
        id (int): Primary key.
        name (str): Unique room name (cannot be null).
        capacity (int): Seating capacity of the room.
        equipment (str): Equipment list stored as text.
        location (str): Human-readable location string.
        available (bool): Room availability status. Defaults to True.
    """
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    equipment = Column(String, nullable=False)
    location = Column(String, nullable=False)
    available = Column(Boolean, default=True)
