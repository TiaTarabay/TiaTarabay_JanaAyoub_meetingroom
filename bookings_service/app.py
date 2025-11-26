"""
Bookings service.

This module implements the REST API for managing meeting room bookings.
It provides endpoints to:

- View all bookings
- Create a new booking
- Update an existing booking
- Cancel a booking
- Check room availability
- Retrieve booking history for a specific user

The service uses SQLAlchemy with a shared PostgreSQL database (configured in
``common.db.connection``) and is exposed as a Flask application.
"""

from flask import Flask, request, jsonify
from datetime import datetime

from functools import wraps
from typing import Optional

from sqlalchemy.orm import Session
from common.db.connection import engine, Base, SessionLocal
from bookings_service.models import Booking
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


MFA_DELETE_BOOKING_CODE = os.environ.get("MFA_DELETE_BOOKING_CODE", "123456")

from flask import request, jsonify

def verify_mfa_for_delete() -> bool:
    """
    Verify MFA code for sensitive booking operations (e.g., delete).

    Expects header: X-MFA-Code
    """
    provided = request.headers.get("X-MFA-Code")
    return provided is not None and provided == MFA_DELETE_BOOKING_CODE

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.environ.get("SENDGRID_FROM_EMAIL", "no-reply@example.com")
print("SENDGRID_API_KEY present:", bool(SENDGRID_API_KEY))
print("SENDGRID_FROM_EMAIL:", SENDGRID_FROM_EMAIL)


def send_booking_email(to_email: str, subject: str, body: str) -> None:
    print(">> send_booking_email called for:", to_email)

    if not SENDGRID_API_KEY:
        print("SENDGRID_API_KEY not set, skipping email send")
        return

    print("Using FROM:", SENDGRID_FROM_EMAIL)

    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body,
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"SendGrid status={response.status_code}")
        print("SendGrid response headers:", response.headers)
    except Exception as e:
        print(f"Error sending email via SendGrid: {e}")



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


# Simple RBAC helpers for Bookings service
def get_current_role() -> str:
    """
    Get the role of the current caller from the HTTP headers.

    In a real system, this would be extracted from a JWT token or API gateway.
    For this project, we use the ``X-Role`` header.

    Possible values: ``admin``, ``regular_user``, ``facility_manager``,
    ``moderator``, ``auditor``, ``service_account``.
    """
    return request.headers.get("X-Role", "regular_user")


def get_current_user_id() -> Optional[int]:
    """
    Get the authenticated user ID from the HTTP headers.

    For demo purposes, we read it from ``X-User-Id``.
    Returns ``None`` if not provided or invalid.
    """
    raw = request.headers.get("X-User-Id")
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def can_do_booking_action(
    role: str,
    action: str,
    *,
    booking_owner_id: Optional[int] = None,
    target_user_id: Optional[int] = None,
) -> bool:
    """
    Central RBAC function for the Bookings service.

    :param role: Current caller role (e.g. ``"admin"``).
    :param action: Logical action name (e.g. ``"get_all"``, ``"create"``,
                   ``"update"``, ``"cancel"``, ``"user_history"``,
                   ``"check_availability"``).
    :param booking_owner_id: User ID that owns the booking (if relevant).
    :param target_user_id: User ID whose history is being requested (if relevant).
    :returns: True if the caller is allowed to perform this action.
    """

    # Admin can do everything on bookings
    if role == "admin":
        return True

    if action == "get_all":
        # Can view all bookings: facility manager + auditor (+ service accounts if needed)
        return role in {"facility_manager", "auditor", "service_account"}

    if action == "create":
        # Regular users and facility managers can create their own bookings
        return role in {"regular_user", "facility_manager", "moderator"}

    if action in {"update", "cancel"}:
        # For update/cancel we need the owner id
        if booking_owner_id is None:
            return False

        if role in {"regular_user", "facility_manager", "moderator"}:
            # Can only update/cancel their own bookings
            current_user_id = get_current_user_id()
            return current_user_id is not None and current_user_id == booking_owner_id

        # Other roles (moderator, auditor, service_account) cannot modify bookings
        return False

    if action == "user_history":
        if role in {"facility_manager", "auditor", "service_account"}:
            # Can see any user's history
            return True
        if role in {"regular_user", "moderator"}:
            # Can only see their own booking history
            current_user_id = get_current_user_id()
            return (
                current_user_id is not None
                and target_user_id is not None
                and current_user_id == target_user_id
            )
        # Others (moderator, service_account) have no access by default
        return False

    if action == "check_availability":
        # Everyone except maybe auditor is allowed; here we allow all roles
        return True

    # Default deny
    return False


@app.route("/bookings", methods=["GET"])
def get_all_bookings():
    """
    Get all bookings.

    **URL:** ``GET /bookings``

    **Method:** ``GET``

    **Description:**
        Returns a list of all bookings with basic information about the user,
        room, time slot, status, and creation time.

    **Responses:**

        - ``200`` – A JSON list of bookings.

    :returns: JSON list of all booking records.
    :rtype: flask.Response
    """
    role = get_current_role()
    if not can_do_booking_action(role, "get_all"):
        return jsonify({"error": "Forbidden"}), 403
    db = get_db()
    try:
        bookings = db.query(Booking).all()
        result = []
        for b in bookings:
            result.append({
                "id": b.id,
                "user_id": b.user_id,
                "room_id": b.room_id,
                "start_time": b.start_time.isoformat(),
                "end_time": b.end_time.isoformat(),
                "status": b.status,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            })
        return jsonify(result), 200
    finally:
        db.close()


@app.route("/bookings", methods=["POST"])
def create_booking():
    """
    Create a new booking.

    **URL:** ``POST /bookings``

    **Method:** ``POST``

    **Description:**
        Creates a new booking for a given user and room if the room is available
        in the requested time interval.

    **Request body (JSON):**

        - ``user_id`` (int): ID of the user making the booking.
        - ``room_id`` (int): ID of the room to be booked.
        - ``start_time`` (str): Start date and time in ISO format
          (e.g. ``"2025-11-23T10:00:00"``).
        - ``end_time`` (str): End date and time in ISO format.

    **Responses:**

        - ``201`` – Booking created successfully. Returns the created booking.
        - ``400`` – Missing fields or invalid date/time values.
        - ``403`` – RBAC: user not allowed to create this booking.
        - ``409`` – Room is already booked in the requested time slot.
    """
    # ---- RBAC: role-level permission ----
    role = get_current_role()
    if not can_do_booking_action(role, "create"):
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    required = ["user_id", "room_id", "start_time", "end_time"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # ---- Self-only check for normal users and moderators ----
    current_user_id = get_current_user_id()
    if role in {"regular_user", "moderator"}:
        body_user_id = int(data["user_id"])
        if current_user_id is None or current_user_id != body_user_id:
            return jsonify({
                "error": "Users can only create bookings for themselves"
            }), 403
    # facility_manager and admin are allowed to create for others

    try:
        start = datetime.fromisoformat(data["start_time"])
        end = datetime.fromisoformat(data["end_time"])
    except ValueError:
        return jsonify({"error": "Invalid datetime format. Use ISO format."}), 400

    if end <= start:
        return jsonify({"error": "end_time must be after start_time"}), 400

    db = get_db()
    try:
        # Check availability: overlapping confirmed booking for same room
        conflict = (
            db.query(Booking)
            .filter(
                Booking.room_id == data["room_id"],
                Booking.status == "CONFIRMED",
                Booking.start_time < end,
                Booking.end_time > start,
            )
            .first()
        )

        if conflict:
            return jsonify({"error": "Room is not available in this time slot"}), 409

        booking = Booking(
            user_id=data["user_id"],
            room_id=data["room_id"],
            start_time=start,
            end_time=end,
            status="CONFIRMED",
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)

        user_email = "jaa102@mail.aub.edu"

        send_booking_email(
            to_email=user_email,
            subject="Booking confirmed",
            body=f"Your booking #{booking.id} for room {booking.room_id} is confirmed on {booking.start_time}."
        )


        return jsonify({
            "id": booking.id,
            "user_id": booking.user_id,
            "room_id": booking.room_id,
            "start_time": booking.start_time.isoformat(),
            "end_time": booking.end_time.isoformat(),
            "status": booking.status,
        }), 201
    finally:
        db.close()



@app.route("/bookings/<int:booking_id>", methods=["PUT"])
def update_booking(booking_id: int):
    """
    Update an existing booking.

    **URL:** ``PUT /bookings/<booking_id>``

    **Method:** ``PUT``

    **Description:**
        Updates the room or time interval of an existing booking.

    **Path parameters:**

        - ``booking_id`` (int): ID of the booking to update.

    **Request body (JSON):**
        All fields are optional and only provided fields are updated.

        - ``room_id`` (int, optional): New room ID.
        - ``start_time`` (str, optional): New start time in ISO format.
        - ``end_time`` (str, optional): New end time in ISO format.

    **Responses:**

        - ``200`` – Booking updated successfully. Returns the updated booking.
        - ``400`` – Invalid time range (end_time <= start_time).
        - ``404`` – Booking with the given ID was not found.

    :param booking_id: ID of the booking to update.
    :type booking_id: int
    :returns: JSON with the updated booking or an error message.
    :rtype: flask.Response
    """
    role = get_current_role()
    data = request.get_json() or {}

    db = get_db()
    try:
        booking = db.query(Booking).get(booking_id)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404
        
        role = get_current_role()
        if not can_do_booking_action(
            role,
            "update",
            booking_owner_id=booking.user_id,
        ):
            return jsonify({"error": "Forbidden"}), 403

        if "room_id" in data and data["room_id"] is not None:
            booking.room_id = data["room_id"]

        if "start_time" in data and data["start_time"]:
            booking.start_time = datetime.fromisoformat(data["start_time"])

        if "end_time" in data and data["end_time"]:
            booking.end_time = datetime.fromisoformat(data["end_time"])

        if booking.end_time <= booking.start_time:
            return jsonify({"error": "end_time must be after start_time"}), 400

        db.commit()
        db.refresh(booking)

        return jsonify({
            "id": booking.id,
            "user_id": booking.user_id,
            "room_id": booking.room_id,
            "start_time": booking.start_time.isoformat(),
            "end_time": booking.end_time.isoformat(),
            "status": booking.status,
        }), 200
    finally:
        db.close()


@app.route("/bookings/<int:booking_id>", methods=["DELETE"])
def cancel_booking(booking_id: int):
    """
    Cancel a booking.

    **URL:** ``DELETE /bookings/<booking_id>``

    **Method:** ``DELETE``

    **Description:**
        Cancels a booking by setting its status to ``CANCELLED``. The record is
        kept in the database so that booking history remains available.

    **Path parameters:**

        - ``booking_id`` (int): ID of the booking to cancel.

    **Responses:**

        - ``200`` – Booking cancelled.
        - ``404`` – Booking not found.

    :param booking_id: ID of the booking to cancel.
    :type booking_id: int
    :returns: JSON confirmation message or error.
    :rtype: flask.Response
    """
    role = get_current_role()
    db = get_db()
    try:
        booking = db.query(Booking).get(booking_id)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404

        role = get_current_role()
        if not can_do_booking_action(
            role,
            "cancel",
            booking_owner_id=booking.user_id,
        ):
            return jsonify({"error": "Forbidden"}), 403
        
        # ---- MFA check for delete ----
        if not verify_mfa_for_delete():
            return jsonify({"error": "MFA required or invalid code"}), 403

        booking.status = "CANCELLED"
        db.commit()

        user_email = "jaa102@mail.aub.edu"

        send_booking_email(
            to_email=user_email,
            subject="Booking cancelled",
            body=f"Your booking #{booking.id} for room {booking.room_id} has been cancelled."
        )

        return jsonify({"message": "Booking cancelled"}), 200
    finally:
        db.close()


@app.route("/availability", methods=["GET"])
def check_availability():
    """
    Check room availability for a given time interval.

    **URL:** ``GET /availability``

    **Method:** ``GET``

    **Description:**
        Checks if a specific room is available between a given start time and
        end time (no overlapping confirmed bookings).

    **Query parameters:**

        - ``room_id`` (int): ID of the room to check.
        - ``start_time`` (str): Start time in ISO format.
        - ``end_time`` (str): End time in ISO format.

    **Responses:**

        - ``200`` – JSON object with ``room_id`` and boolean ``available``.
        - ``400`` – Missing or invalid parameters.

    :returns: JSON with room ID and availability flag.
    :rtype: flask.Response
    """
    role = get_current_role()
    if not can_do_booking_action(role, "check_availability"):
        return jsonify({"error": "Forbidden"}), 403

    room_id = request.args.get("room_id")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")

    if not (room_id and start_time and end_time):
        return jsonify({"error": "room_id, start_time and end_time are required"}), 400

    try:
        room_id_int = int(room_id)
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid parameters"}), 400

    if end <= start:
        return jsonify({"error": "end_time must be after start_time"}), 400

    db = get_db()
    try:
        conflict = (
            db.query(Booking)
            .filter(
                Booking.room_id == room_id_int,
                Booking.status == "CONFIRMED",
                Booking.start_time < end,
                Booking.end_time > start,
            )
            .first()
        )

        available = conflict is None
        return jsonify({"room_id": room_id_int, "available": available}), 200
    finally:
        db.close()


@app.route("/bookings/user/<int:user_id>", methods=["GET"])
def get_user_booking_history(user_id: int):
    """
    Get booking history for a user.

    **URL:** ``GET /bookings/user/<user_id>``

    **Method:** ``GET``

    **Description:**
        Returns all bookings for a given user, ordered by start time in
        descending order.

    **Path parameters:**

        - ``user_id`` (int): ID of the user whose booking history is requested.

    **Responses:**

        - ``200`` – List of bookings associated with the user.

    :param user_id: ID of the user.
    :type user_id: int
    :returns: JSON list of bookings for the given user.
    :rtype: flask.Response
    """
    role = get_current_role()
    if not can_do_booking_action(
        role,
        "user_history",
        target_user_id=user_id,
    ):
        return jsonify({"error": "Forbidden"}), 403
    db = get_db()
    try:
        bookings = (
            db.query(Booking)
            .filter(Booking.user_id == user_id)
            .order_by(Booking.start_time.desc())
            .all()
        )

        result = []
        for b in bookings:
            result.append({
                "id": b.id,
                "room_id": b.room_id,
                "start_time": b.start_time.isoformat(),
                "end_time": b.end_time.isoformat(),
                "status": b.status,
            })
        return jsonify(result), 200
    finally:
        db.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
