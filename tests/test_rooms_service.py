def test_add_room(client_rooms, admin_token):
    response = client_rooms.post(
        "/rooms/",
        json={
            "name": "Room A",
            "capacity": 10,
            "equipment": "TV, Projector",
            "location": "Building 1",
            "available": True
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Room A"


def test_get_rooms(client_rooms):
    response = client_rooms.get("/rooms/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)



def test_get_all_rooms_empty(client_rooms):
    res = client_rooms.get("/rooms/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_add_room_missing_field(client_rooms, admin_token):
    res = client_rooms.post(
        "/rooms/",
        json={
            "name": "BadRoom"
            # missing capacity, equipment, location
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 422


def test_get_room_invalid_id(client_rooms):
    res = client_rooms.get("/rooms/999999")
    assert res.status_code in (400, 404)
