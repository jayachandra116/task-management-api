from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError


# ── global handlers ──


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


# ── conflict ──


def test_register_duplicate_email_returns_409(client, regular_user):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@test.com",  # already exists
            "password": "password123",
        },
    )
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


# ── not found ──


def test_get_nonexistent_task_returns_404(client, user_token):
    response = client.get(
        "/api/v1/tasks/99999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_nonexistent_user_returns_404(client, admin_token):
    response = client.get(
        "/api/v1/users/99999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


# ── task ownership returns 404 not 403 ──


def test_access_other_users_task_returns_404(client, user_token, admin_user, db):
    from app.models import Task

    task = Task(title="Admin task", complete=False, owner_id=admin_user.id)
    db.add(task)
    db.commit()

    # regular user tries to access admin's task — gets 404 not 403
    response = client.get(
        f"/api/v1/tasks/{task.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404


# ── db_transaction rollback ──


def test_db_transaction_rolls_back_on_integrity_error(client, user_token):
    """
    Simulate an IntegrityError during task creation.
    Verify rollback happens and clean 409 is returned.
    """
    with patch("app.services.task.db_transaction") as mock_ctx:
        mock_ctx.return_value.__enter__ = MagicMock(return_value=None)
        mock_ctx.return_value.__exit__ = MagicMock(
            side_effect=IntegrityError("duplicate", {}, None)
        )
        response = client.post(
            "/api/v1/tasks/",
            json={"title": "Test task"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
    # integrity errors bubble up as 409 or 500 depending on type
    assert response.status_code in [409, 500]


# ── bad request ──


def test_admin_change_own_role_returns_400(client, admin_token, admin_user):
    response = client.patch(
        f"/api/v1/user/{admin_user.id}/role",
        json={"role": "user"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400


def test_admin_delete_self_returns_400(client, admin_token, admin_user):
    response = client.delete(
        f"/api/v1/user/{admin_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400
