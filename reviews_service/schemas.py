"""
Schemas for the Reviews service.

This module defines simple dataclasses that represent the input data
for creating and updating reviews through the API.
"""

from dataclasses import dataclass


@dataclass
class ReviewCreate:
    """
    Data required to submit a new review.

    This schema represents the JSON body expected by the
    ``POST /reviews`` endpoint.

    Attributes
    ----------
    user_id : int
        ID of the user writing the review.
    room_id : int
        ID of the room being reviewed.
    rating : int
        Rating given to the room (for example from 1 to 5).
    comment : str
        Optional free text comment about the room or the experience.
    """
    user_id: int
    room_id: int
    rating: int
    comment: str | None = None


@dataclass
class ReviewUpdate:
    """
    Data used to update an existing review.

    This schema represents the optional fields that can be sent to the
    ``PUT /reviews/<review_id>`` endpoint. Only the fields that are
    provided will be updated.

    Attributes
    ----------
    rating : int | None
        New rating value, or ``None`` to keep the current rating.
    comment : str | None
        New comment text, or ``None`` to keep the current comment.
    """
    rating: int | None = None
    comment: str | None = None
