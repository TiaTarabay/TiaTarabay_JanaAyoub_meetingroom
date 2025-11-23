"""
Database models for the Reviews service.

This module defines the SQLAlchemy ORM model used by the Reviews service.
The main entity is ``Review``, which represents feedback from a user about
a specific meeting room.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from common.db.connection import Base


class Review(Base):
    """
    Review model.

    This model represents a single review left by a user for a room.
    It includes a rating, an optional comment, a status, and a flag that
    can be used by moderators to mark inappropriate reviews.

    **Table name:** ``reviews``

    **Main fields:**

    - ``id``: Primary key, unique identifier for each review.
    - ``user_id``: ID of the user who wrote the review.
    - ``room_id``: ID of the room being reviewed.
    - ``rating``: Integer score, for example from 1 to 5.
    - ``comment``: Free text comment about the room or the experience.
    - ``status``: Current status of the review (e.g. ``ACTIVE``, ``DELETED``).
    - ``is_flagged``: Boolean indicating if the review was flagged as inappropriate.
    - ``created_at``: Timestamp when the review was created.

    The Reviews service uses this model to store, update, and moderate
    feedback about meeting rooms.
    """

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    room_id = Column(Integer, index=True, nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String(500), nullable=True)
    status = Column(String(20), default="ACTIVE")  # e.g. ACTIVE / DELETED
    is_flagged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
