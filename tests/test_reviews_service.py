import json


def _make_headers(role: str, user_id: int) -> dict:
    """
    Build standard HTTP headers for Reviews API tests.

    The headers include:
    - X-Role: the caller's role (e.g. "regular_user", "moderator").
    - X-User-Id: the numeric user identifier used by the RBAC layer.
    - Content-Type: set to "application/json" so Flask parses the body as JSON.

    :param role: Name of the role to use in the request.
    :param user_id: ID of the user performing the request.
    :returns: Dictionary of HTTP headers for the test client.
    """
    return {
        "X-Role": role,
        "X-User-Id": str(user_id),
        "Content-Type": "application/json",
    }


def test_user_can_create_review_for_self(reviews_client):
    """
    Test that a regular user can create a review only on their own behalf.

    The test sends POST /reviews with user_id equal to the X-User-Id header
    and expects HTTP 201 and the created review in the response payload.
    """
    body = {
        "user_id": 10,
        "room_id": 1,
        "rating": 4,
        "comment": "Nice room",
    }
    res = reviews_client.post(
        "/reviews",
        data=json.dumps(body),
        headers=_make_headers("regular_user", 10),
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["user_id"] == 10
    assert data["room_id"] == 1
    assert data["rating"] == 4


def test_user_cannot_create_review_for_someone_else(reviews_client):
    """
    Test that a regular user cannot create a review for another user.

    When the body.user_id differs from X-User-Id, the service should reject
    the request with HTTP 403 and an appropriate error message.
    """
    body = {
        "user_id": 20,
        "room_id": 1,
        "rating": 5,
        "comment": "Fake review",
    }
    res = reviews_client.post(
        "/reviews",
        data=json.dumps(body),
        headers=_make_headers("regular_user", 10),
    )
    assert res.status_code == 403
    assert "create reviews for themselves" in res.get_json()["error"]


def test_owner_and_moderator_update_delete_review(reviews_client):
    """
    Test that the review owner can update their own review, and the moderator
    can update and delete any review.

    Steps:
    - A regular user (user_id=10) creates a review.
    - The owner updates the rating successfully.
    - A different regular user is forbidden from updating it.
    - A moderator can update the comment and then delete the review.
    """
    # User 10 creates review
    body = {
        "user_id": 10,
        "room_id": 2,
        "rating": 3,
        "comment": "Average",
    }
    res_create = reviews_client.post(
        "/reviews",
        data=json.dumps(body),
        headers=_make_headers("regular_user", 10),
    )
    assert res_create.status_code == 201
    review_id = res_create.get_json()["id"]

    # Owner updates -> OK
    res_owner_update = reviews_client.put(
        f"/reviews/{review_id}",
        data=json.dumps({"rating": 4}),
        headers=_make_headers("regular_user", 10),
    )
    assert res_owner_update.status_code == 200
    assert res_owner_update.get_json()["rating"] == 4

    # Other user tries to update -> Forbidden
    res_other_update = reviews_client.put(
        f"/reviews/{review_id}",
        data=json.dumps({"rating": 1}),
        headers=_make_headers("regular_user", 99),
    )
    assert res_other_update.status_code == 403

    # Moderator updates -> OK (global moderation power)
    res_mod_update = reviews_client.put(
        f"/reviews/{review_id}",
        data=json.dumps({"comment": "Edited by moderator"}),
        headers=_make_headers("moderator", 50),
    )
    assert res_mod_update.status_code == 200
    assert res_mod_update.get_json()["comment"] == "Edited by moderator"

    # Moderator deletes -> OK
    res_mod_delete = reviews_client.delete(
        f"/reviews/{review_id}",
        headers=_make_headers("moderator", 50),
    )
    assert res_mod_delete.status_code == 200
    assert res_mod_delete.get_json()["message"] == "Review deleted"


def test_moderator_can_flag_but_user_cannot(reviews_client):
    """
    Test that only a moderator (or admin) can flag a review as inappropriate.

    A regular user attempting POST /reviews/<id>/flag should receive HTTP 403,
    while the same request from a moderator should succeed and set is_flagged
    to True for that review.
    """
    # Create a review
    body = {
        "user_id": 10,
        "room_id": 3,
        "rating": 2,
        "comment": "Toxic review",
    }
    res_create = reviews_client.post(
        "/reviews",
        data=json.dumps(body),
        headers=_make_headers("regular_user", 10),
    )
    assert res_create.status_code == 201
    review_id = res_create.get_json()["id"]

    # Regular user tries to flag -> Forbidden
    res_user_flag = reviews_client.post(
        f"/reviews/{review_id}/flag",
        headers=_make_headers("regular_user", 10),
    )
    assert res_user_flag.status_code == 403

    # Moderator flags -> OK
    res_mod_flag = reviews_client.post(
        f"/reviews/{review_id}/flag",
        headers=_make_headers("moderator", 50),
    )
    assert res_mod_flag.status_code == 200
    assert res_mod_flag.get_json()["is_flagged"] is True


def test_auditor_and_service_account_read_only_on_reviews(reviews_client):
    """
    Test that the auditor and service_account roles have read-only access.

    Both roles should be able to list reviews for a room, but they must not
    be able to delete reviews. The test verifies that GET /reviews/room/<id>
    returns data, and DELETE /reviews/<id> as auditor returns HTTP 403.
    """
    # Create data
    res_create = reviews_client.post(
        "/reviews",
        data=json.dumps({
            "user_id": 10,
            "room_id": 4,
            "rating": 5,
            "comment": "Great!",
        }),
        headers=_make_headers("regular_user", 10),
    )
    assert res_create.status_code == 201

    # Auditor can list room reviews
    res_aud = reviews_client.get(
        "/reviews/room/4",
        headers=_make_headers("auditor", 99),
    )
    assert res_aud.status_code == 200
    assert len(res_aud.get_json()) >= 1

    # Service account can list room reviews
    res_sa = reviews_client.get(
        "/reviews/room/4",
        headers=_make_headers("service_account", 999),
    )
    assert res_sa.status_code == 200

    # But auditor cannot delete
    review_id = res_create.get_json()["id"]
    res_aud_del = reviews_client.delete(
        f"/reviews/{review_id}",
        headers=_make_headers("auditor", 99),
    )
    assert res_aud_del.status_code == 403
