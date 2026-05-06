def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "new@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new@test.com"
    assert "password" not in response.json()


def test_register_duplicate_email(client, regular_user):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "user@test.com", "password": "password123"},
    )
    assert response.status_code == 400


def test_login_success(client, regular_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user@test.com", "password": "testpass123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client, regular_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
