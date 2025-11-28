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



def test_register_missing_field(client_users):
    res = client_users.post("/users/register", json={
        "username": "abc"
        # missing email + password
    })
    assert res.status_code == 422


def test_login_missing_password(client_users):
    res = client_users.post("/users/login", json={
        "username": "admin_test"
        # missing password
    })
    assert res.status_code == 422


def test_get_current_user(client_users, create_admin, admin_token):
    res = client_users.get(
        "/users/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    assert res.json()["username"] == "admin_test"

