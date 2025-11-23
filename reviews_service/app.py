"""
Reviews service.

This module implements the REST API for managing reviews of meeting rooms.
It provides endpoints to:

- Submit a new review for a room
- Update an existing review
- Delete (soft delete) a review
- Retrieve reviews for a specific room
- Flag a review as inappropriate (moderation)

The service uses SQLAlchemy with a shared database configuration from
``common.db.connection`` and is exposed as a Flask application.
"""

from flask import Flask, request, jsonify
from sqlalchemy.orm import Session

from common.db.connection import engine, Base, SessionLocal
from reviews_service.models import Review

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = Flask(__name__)


def get_db() -> Session:
    """
    Get a new database session.

    This helper function returns a SQLAlchemy session. The caller is responsible
    for closing the session after use.

    :returns: A SQLAlchemy session bound to the main application engine.
    :rtype: sqlalchemy.orm.Session
    """
    db = SessionLocal()
    return db


@app.route("/reviews", methods=["POST"])
def create_review():
    """
    Submit a new review for a meeting room.

    **URL:** ``POST /reviews``

    **Method:** ``POST``

    **Description:**
        Creates a new review for a specific room written by a user.
        Each review contains a rating and an optional comment.

    **Request body (JSON):**

        - ``user_id`` (int, required): ID of the user writing the review.
        - ``room_id`` (int, required): ID of the room being reviewed.
        - ``rating`` (int, required): Rating value (e.g. 1 to 5).
        - ``comment`` (str, optional): Free text comment.

    **Responses:**

        - ``201 Created``: Review created successfully.
        - ``400 Bad Request``: Missing or invalid fields.

    :returns: JSON with the created review or an error message.
    :rtype: flask.Response
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    required = ["user_id", "room_id", "rating"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        rating = int(data["rating"])
    except (TypeError, ValueError):
        return jsonify({"error": "rating must be an integer"}), 400

    if rating < 1 or rating > 5:
        return jsonify({"error": "rating must be between 1 and 5"}), 400

    db = get_db()
    try:
        review = Review(
            user_id=data["user_id"],
            room_id=data["room_id"],
            rating=rating,
            comment=data.get("comment"),
            status="ACTIVE",
            is_flagged=False,
        )
        db.add(review)
        db.commit()
        db.refresh(review)

        return jsonify({
            "id": review.id,
            "user_id": review.user_id,
            "room_id": review.room_id,
            "rating": review.rating,
            "comment": review.comment,
            "status": review.status,
            "is_flagged": review.is_flagged,
            "created_at": review.created_at.isoformat() if review.created_at else None,
        }), 201
    finally:
        db.close()


@app.route("/reviews/<int:review_id>", methods=["PUT"])
def update_review(review_id: int):
    """
    Update an existing review.

    **URL:** ``PUT /reviews/<review_id>``

    **Method:** ``PUT``

    **Description:**
        Updates the rating and/or comment of an existing review.

    **Path parameters:**

        - ``review_id`` (int): ID of the review to update.

    **Request body (JSON):**

        Optional fields:
        - ``rating`` (int): New rating value (1 to 5).
        - ``comment`` (str): New comment text.

    **Responses:**

        - ``200 OK``: Review updated successfully.
        - ``400 Bad Request``: Invalid rating.
        - ``404 Not Found``: Review does not exist.

    :param review_id: ID of the review to update.
    :type review_id: int
    :returns: JSON with the updated review or an error message.
    :rtype: flask.Response
    """
    data = request.get_json() or {}

    db = get_db()
    try:
        review = db.query(Review).get(review_id)
        if not review or review.status == "DELETED":
            return jsonify({"error": "Review not found"}), 404

        if "rating" in data and data["rating"] is not None:
            try:
                rating = int(data["rating"])
            except (TypeError, ValueError):
                return jsonify({"error": "rating must be an integer"}), 400
            if rating < 1 or rating > 5:
                return jsonify({"error": "rating must be between 1 and 5"}), 400
            review.rating = rating

        if "comment" in data:
            review.comment = data["comment"]

        db.commit()
        db.refresh(review)

        return jsonify({
            "id": review.id,
            "user_id": review.user_id,
            "room_id": review.room_id,
            "rating": review.rating,
            "comment": review.comment,
            "status": review.status,
            "is_flagged": review.is_flagged,
            "created_at": review.created_at.isoformat() if review.created_at else None,
        }), 200
    finally:
        db.close()


@app.route("/reviews/<int:review_id>", methods=["DELETE"])
def delete_review(review_id: int):
    """
    Delete (soft delete) a review.

    **URL:** ``DELETE /reviews/<review_id>``

    **Method:** ``DELETE``

    **Description:**
        Marks a review as ``DELETED`` instead of physically deleting the row
        from the database. This keeps historical data available if needed.

    **Path parameters:**

        - ``review_id`` (int): ID of the review to delete.

    **Responses:**

        - ``200 OK``: Review deleted (status set to ``DELETED``).
        - ``404 Not Found``: Review not found.

    :param review_id: ID of the review to delete.
    :type review_id: int
    :returns: JSON confirmation message or error.
    :rtype: flask.Response
    """
    db = get_db()
    try:
        review = db.query(Review).get(review_id)
        if not review or review.status == "DELETED":
            return jsonify({"error": "Review not found"}), 404

        review.status = "DELETED"
        db.commit()
        return jsonify({"message": "Review deleted"}), 200
    finally:
        db.close()


@app.route("/reviews/room/<int:room_id>", methods=["GET"])
def get_reviews_for_room(room_id: int):
    """
    Retrieve reviews for a specific room.

    **URL:** ``GET /reviews/room/<room_id>``

    **Method:** ``GET``

    **Description:**
        Returns all active reviews for the given room. Deleted reviews
        are not included.

    **Path parameters:**

        - ``room_id`` (int): ID of the room whose reviews are requested.

    **Responses:**

        - ``200 OK``: List of reviews for the room.

    :param room_id: Room ID whose reviews are requested.
    :type room_id: int
    :returns: JSON list of reviews for the specified room.
    :rtype: flask.Response
    """
    db = get_db()
    try:
        reviews = (
            db.query(Review)
            .filter(Review.room_id == room_id, Review.status == "ACTIVE")
            .order_by(Review.created_at.desc())
            .all()
        )

        result = []
        for r in reviews:
            result.append({
                "id": r.id,
                "user_id": r.user_id,
                "room_id": r.room_id,
                "rating": r.rating,
                "comment": r.comment,
                "status": r.status,
                "is_flagged": r.is_flagged,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })
        return jsonify(result), 200
    finally:
        db.close()


@app.route("/reviews/<int:review_id>/flag", methods=["POST"])
def flag_review(review_id: int):
    """
    Flag a review as inappropriate (moderation).

    **URL:** ``POST /reviews/<review_id>/flag``

    **Method:** ``POST``

    **Description:**
        Sets the ``is_flagged`` field of the review to ``True``. In a real
        system, this endpoint would typically be restricted to moderator
        or admin roles. Here we only implement the basic moderation action.

    **Path parameters:**

        - ``review_id`` (int): ID of the review to flag.

    **Responses:**

        - ``200 OK``: Review flagged successfully.
        - ``404 Not Found``: Review not found.

    :param review_id: ID of the review to flag.
    :type review_id: int
    :returns: JSON with the updated review or an error message.
    :rtype: flask.Response
    """
    db = get_db()
    try:
        review = db.query(Review).get(review_id)
        if not review or review.status == "DELETED":
            return jsonify({"error": "Review not found"}), 404

        review.is_flagged = True
        db.commit()
        db.refresh(review)

        return jsonify({
            "id": review.id,
            "user_id": review.user_id,
            "room_id": review.room_id,
            "rating": review.rating,
            "comment": review.comment,
            "status": review.status,
            "is_flagged": review.is_flagged,
            "created_at": review.created_at.isoformat() if review.created_at else None,
        }), 200
    finally:
        db.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
