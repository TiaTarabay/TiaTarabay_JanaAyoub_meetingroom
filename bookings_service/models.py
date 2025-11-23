"""
Database models for the Bookings service.

This module defines the SQLAlchemy ORM model used by the Bookings service.
The main entity is ``Booking``, which represents a single reservation of a
meeting room by a user for a specific time interval.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from common.db.connection import Base


class Booking(Base):
    """
    Booking model.

    This model represents a single meeting room booking. Each booking links
    a user to a room for a given time interval, and stores a status flag
    (e.g. ``CONFIRMED`` or ``CANCELLED``) as well as a creation timestamp.

    **Table name:** ``bookings``

    **Main fields:**

    - ``id``: Primary key, unique identifier for each booking.
    - ``user_id``: ID of the user who made the booking.
    - ``room_id``: ID of the room that is being booked.
    - ``start_time``: Start date and time of the booking.
    - ``end_time``: End date and time of the booking.
    - ``status``: Current status of the booking (default ``CONFIRMED``).
    - ``created_at``: Timestamp when the booking was created.

    This model is mapped to the database using SQLAlchemy and is used by
    the Bookings API in ``bookings_service.app``.
    """

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    room_id = Column(Integer, index=True, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="CONFIRMED")  # e.g. CONFIRMED / CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow)
