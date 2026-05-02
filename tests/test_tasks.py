def test_create_task(client, user_token):
    response = client.post(
        "/tasks/",
        json={"title": "Test task", "description": "Test desc"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test task"
    assert response.json()["complete"] is False


def test_list_tasks_paginated(client, user_token):
    # create 3 tasks
    for i in range(3):
        client.post(
            "/tasks/",
            json={"title": f"Task {i}"},
            headers={"Authorization": f"Bearer {user_token}"},
        )

    response = client.get(
        "/tasks/?page=1&size=2",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["meta"]["total_items"] == 3
    assert data["meta"]["has_next"] is True


def test_filter_tasks_by_complete(client, user_token):
    client.post(
        "/tasks/",
        json={"title": "Task A"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    response = client.get(
        "/tasks/?complete=false",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert all(not t["complete"] for t in response.json()["items"])


def test_filter_tasks_by_search(client, user_token):
    client.post(
        "/tasks/",
        json={"title": "Fix login bug"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    client.post(
        "/tasks/",
        json={"title": "Write docs"},
        headers={"Authorization": f"Bearer {user_token}"},
    )

    response = client.get(
        "/tasks/?search=bug",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert "bug" in response.json()["items"][0]["title"].lower()


def test_delete_task_unauthorized(client, user_token, admin_user, db):
    from app.models import Task

    task = Task(title="Admin task", complete=False, owner_id=admin_user.id)
    db.add(task)
    db.commit()

    response = client.delete(
        f"/tasks/{task.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
