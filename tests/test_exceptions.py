def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_validation_error_returns_clean_response(client):
    """422 response should have structured errors list."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",  # invalid email
            "password": "short",  # too short
        },
    )
    assert response.status_code == 422
    body = response.json()
    assert "errors" in body
    assert "detail" in body
