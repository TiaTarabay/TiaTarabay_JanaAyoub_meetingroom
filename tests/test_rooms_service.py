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
