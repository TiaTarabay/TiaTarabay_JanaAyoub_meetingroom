def test_login_user(client_users, create_admin):
    response = client_users.post(
        "/users/login",
        json={"username": "admin_test", "password": "adminpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_register_user(client_users):
    response = client_users.post(
        "/users/register",
        json={
            "username": "user1",
            "email": "user1@test.com",
            "password": "pass123"
        }
    )
    assert response.status_code == 200
    assert response.json()["username"] == "user1"


def test_get_all_users(client_users, admin_token):
    response = client_users.get(
        "/users/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
