def test_get_own_profile(client, user_token, regular_user):
    response = client.get("/api/v1/user/me", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == regular_user.email
    assert "password" not in response.json()


def test_change_password_success(client, user_token):
    response = client.patch(
        "/api/v1/user/me/password",
        json={
            "current_password": "testpass123",
            "new_password": "newpass456",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 204


def test_change_password_wrong_current(client, user_token):
    response = client.patch(
        "/api/v1/user/me/password",
        json={
            "current_password": "wrongpass",
            "new_password": "newpass456",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 401


def test_list_users_as_admin(client, admin_token):
    response = client.get(
        "/api/v1/user/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "items" in response.json()


def test_list_users_as_regular_user(client, user_token):
    response = client.get(
        "/api/v1/user/",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 401
