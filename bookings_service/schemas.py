"""
Schemas for the Bookings service.

This module defines simple dataclasses that represent the input data
for creating and updating bookings through the API. They are used as
a clear structure for request payloads, even though the current
implementation reads JSON directly from Flask's ``request`` object.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class BookingCreate:
    """
    Data required to create a new booking.

    This schema represents the JSON body expected by the
    ``POST /bookings`` endpoint.

    Attributes
    ----------
    user_id : int
        ID of the user making the booking.
    room_id : int
        ID of the room to be booked.
    start_time : str
        Start date and time in ISO format, for example
        ``"2025-11-23T10:00:00"``.
    end_time : str
        End date and time in ISO format.
    """
    user_id: int
    room_id: int
    start_time: str 
    end_time: str


@dataclass
class BookingUpdate:
    """
    Data used to update an existing booking.

    This schema represents the optional fields that can be sent to the
    ``PUT /bookings/<booking_id>`` endpoint. Only the fields that are
    provided will be updated.

    Attributes
    ----------
    room_id : int | None
        New room ID, or ``None`` to keep the current room.
    start_time : str | None
        New start time in ISO format, or ``None`` to keep the current value.
    end_time : str | None
        New end time in ISO format, or ``None`` to keep the current value.
    """
    room_id: int | None = None
    start_time: str | None = None
    end_time: str | None = None
