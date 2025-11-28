import json

def _make_headers(role: str, user_id: int) -> dict:
    """
    Build a standard headers dictionary for API test calls.

    The headers include the caller role (X-Role), the user identifier
    (X-User-Id), and JSON content type so that the Flask app interprets
    the request body as JSON.
    """
    return {
        "X-Role": role,
        "X-User-Id": str(user_id),
        "Content-Type": "application/json",
    }


def test_admin_can_get_all_bookings(bookings_client):
    """
    Test that an admin can retrieve the full list of bookings.

    The test first creates a booking as a regular user, then performs
    a GET /bookings request as an admin and verifies that the booking
    appears in the resulting list.
    """
    body = {
        "user_id": 10,
        "room_id": 1,
        "start_time": "2025-11-26T10:00:00",
        "end_time": "2025-11-26T11:00:00",
    }
    res_create = bookings_client.post(
        "/bookings",
        data=json.dumps(body),
        headers=_make_headers("regular_user", 10),
    )
    assert res_create.status_code == 201

    res = bookings_client.get(
        "/bookings",
        headers=_make_headers("admin", 1),
    )
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert any(b["user_id"] == 10 for b in data)


def test_regular_user_cannot_get_all_bookings(bookings_client):
    """
    Test that a regular user is forbidden from listing all bookings.

    A GET /bookings request with role=regular_user should return
    HTTP 403 and a JSON error message.
    """
    res = bookings_client.get(
        "/bookings",
        headers=_make_headers("regular_user", 10),
    )
    assert res.status_code == 403
    assert res.get_json()["error"] == "Forbidden"


def test_regular_user_can_only_create_booking_for_self(bookings_client):
    """
    Test that a regular user can only create bookings on their own behalf.

    When the user_id in the request body matches the X-User-Id header,
    the booking is created successfully. If they differ, the API should
    return HTTP 403.
    """
    start = "2025-11-26T12:00:00"
    end = "2025-11-26T13:00:00"

    # OK: body.user_id == header user_id
    res_ok = bookings_client.post(
        "/bookings",
        data=json.dumps({
            "user_id": 10,
            "room_id": 1,
            "start_time": start,
            "end_time": end,
        }),
        headers=_make_headers("regular_user", 10),
    )
    assert res_ok.status_code == 201

    # NOT OK: mismatch between body.user_id and header user_id
    res_forbidden = bookings_client.post(
        "/bookings",
        data=json.dumps({
            "user_id": 20,
            "room_id": 1,
            "start_time": start,
            "end_time": end,
        }),
        headers=_make_headers("regular_user", 10),
    )
    assert res_forbidden.status_code == 403
    assert "create bookings for themselves" in res_forbidden.get_json()["error"]


def test_user_can_update_own_booking_but_not_others(bookings_client):
    """
    Test that a user may update only their own bookings but not others'.

    The test creates a booking for user 10, verifies that user 10 can
    update it, and that another user (user 20) receives HTTP 403 when
    attempting the same update.
    """
    body = {
        "user_id": 10,
        "room_id": 1,
        "start_time": "2025-11-26T14:00:00",
        "end_time": "2025-11-26T15:00:00",
    }
    res_create = bookings_client.post(
        "/bookings",
        data=json.dumps(body),
        headers=_make_headers("regular_user", 10),
    )
    assert res_create.status_code == 201
    booking_id = res_create.get_json()["id"]

    res_owner = bookings_client.put(
        f"/bookings/{booking_id}",
        data=json.dumps({"end_time": "2025-11-26T15:30:00"}),
        headers=_make_headers("regular_user", 10),
    )
    assert res_owner.status_code == 200
    assert res_owner.get_json()["end_time"].endswith("15:30:00")

    res_other = bookings_client.put(
        f"/bookings/{booking_id}",
        data=json.dumps({"end_time": "2025-11-26T16:00:00"}),
        headers=_make_headers("regular_user", 20),
    )
    assert res_other.status_code == 403
    assert res_other.get_json()["error"] == "Forbidden"


def test_admin_can_force_cancel_any_booking(bookings_client):
    """
    Test that an admin can cancel any booking regardless of its owner.

    The test creates a booking for a regular user and then cancels it
    using DELETE /bookings/<id> with role=admin, which should succeed.
    """
    body = {
        "user_id": 10,
        "room_id": 2,
        "start_time": "2025-11-26T16:00:00",
        "end_time": "2025-11-26T17:00:00",
    }
    res_create = bookings_client.post(
        "/bookings",
        data=json.dumps(body),
        headers=_make_headers("regular_user", 10),
    )
    assert res_create.status_code == 201
    booking_id = res_create.get_json()["id"]

    res_admin = bookings_client.delete(
        f"/bookings/{booking_id}",
        headers=_make_headers("admin", 1),
    )
    assert res_admin.status_code == 200
    assert res_admin.get_json()["message"] == "Booking cancelled"


def test_auditor_and_service_account_are_read_only(bookings_client):
    """
    Test that the auditor and service_account roles are strictly read-only.

    Both roles should be able to read bookings data but should be denied
    when attempting to cancel a booking.
    """
    body = {
        "user_id": 10,
        "room_id": 3,
        "start_time": "2025-11-26T18:00:00",
        "end_time": "2025-11-26T19:00:00",
    }
    res_create = bookings_client.post(
        "/bookings",
        data=json.dumps(body),
        headers=_make_headers("regular_user", 10),
    )
    assert res_create.status_code == 201
    booking_id = res_create.get_json()["id"]

    res_aud_read = bookings_client.get(
        "/bookings",
        headers=_make_headers("auditor", 99),
    )
    assert res_aud_read.status_code == 200

    res_sa_read = bookings_client.get(
        "/bookings",
        headers=_make_headers("service_account", 999),
    )
    assert res_sa_read.status_code == 200

    res_aud_del = bookings_client.delete(
        f"/bookings/{booking_id}",
        headers=_make_headers("auditor", 99),
    )
    assert res_aud_del.status_code == 403

    res_sa_del = bookings_client.delete(
        f"/bookings/{booking_id}",
        headers=_make_headers("service_account", 999),
    )
    assert res_sa_del.status_code == 403
