from tests.conftest import API, login, register


def test_login_and_me(client, admin):
    headers = login(client, "admin@example.com", "adminpass")
    r = client.get(f"{API}/users/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["is_admin"] is True


def test_login_wrong_password(client, admin):
    r = client.post(f"{API}/auth/login", data={"username": "admin", "password": "wrong-pass"})
    assert r.status_code == 401


def test_requires_auth(client):
    assert client.get(f"{API}/tasks").status_code == 401


def test_admin_manages_companies_and_users(client, admin):
    h = login(client, "admin", "adminpass")

    r = client.post(f"{API}/companies", json={"name": "NashTech", "rating": 4.5}, headers=h)
    assert r.status_code == 201, r.text
    company_id = r.json()["id"]
    assert r.json()["mode"] == "ACTIVE"

    assert client.post(f"{API}/companies", json={"name": "nashtech"}, headers=h).status_code == 409
    assert client.post(f"{API}/companies", json={"name": "X", "rating": 6}, headers=h).status_code == 422

    r = client.post(
        f"{API}/users",
        json={
            "email": "Bob@Example.com",
            "username": "bob",
            "first_name": "Bob",
            "last_name": "Smith",
            "password": "bobpassword",
            "company_id": company_id,
        },
        headers=h,
    )
    assert r.status_code == 201, r.text
    assert r.json()["email"] == "bob@example.com"
    bob_id = r.json()["id"]

    r = client.get(f"{API}/users", params={"company_id": company_id}, headers=h)
    assert r.json()["total"] == 1

    bob = login(client, "bob", "bobpassword")
    assert client.post(f"{API}/companies", json={"name": "Other"}, headers=bob).status_code == 403
    assert client.get(f"{API}/users", headers=bob).status_code == 403
    assert client.get(f"{API}/companies/{company_id}", headers=bob).status_code == 200

    r = client.patch(f"{API}/users/{bob_id}", json={"is_active": False}, headers=h)
    assert r.json()["is_active"] is False
    assert client.get(f"{API}/users/me", headers=bob).status_code == 403

    assert client.delete(f"{API}/companies/{company_id}", headers=h).status_code == 204
    assert client.get(f"{API}/users/{bob_id}", headers=h).json()["company_id"] is None


def test_task_ownership_and_crud(client, admin):
    alice = register(client, "alice")
    carol = register(client, "carol")

    r = client.post(f"{API}/tasks", json={"summary": "Write report", "priority": "HIGH"}, headers=alice)
    assert r.status_code == 201, r.text
    task = r.json()
    assert task["status"] == "NEW"

    client.post(f"{API}/tasks", json={"summary": "Carol task"}, headers=carol)

    r = client.get(f"{API}/tasks", headers=alice)
    assert r.json()["total"] == 1

    assert client.get(f"{API}/tasks/{task['id']}", headers=carol).status_code == 404
    assert client.patch(f"{API}/tasks/{task['id']}", json={"summary": "x"}, headers=carol).status_code == 404

    r = client.patch(f"{API}/tasks/{task['id']}", json={"status": "DONE"}, headers=alice)
    assert r.json()["status"] == "DONE"
    assert client.patch(f"{API}/tasks/{task['id']}", json={"summary": None}, headers=alice).status_code == 422

    r = client.post(
        f"{API}/tasks", json={"summary": "Steal", "owner_id": task["owner_id"]}, headers=carol
    )
    assert r.status_code == 403

    h = login(client, "admin", "adminpass")
    assert client.get(f"{API}/tasks", headers=h).json()["total"] == 2
    r = client.get(f"{API}/tasks", params={"status": "DONE"}, headers=h)
    assert r.json()["total"] == 1

    assert client.delete(f"{API}/tasks/{task['id']}", headers=alice).status_code == 204
    assert client.get(f"{API}/tasks", headers=alice).json()["total"] == 0


def test_change_password(client):
    h = register(client, "dave", "oldpassword")
    r = client.put(
        f"{API}/users/me/password",
        json={"current_password": "wrong", "new_password": "newpassword"},
        headers=h,
    )
    assert r.status_code == 400
    r = client.put(
        f"{API}/users/me/password",
        json={"current_password": "oldpassword", "new_password": "newpassword"},
        headers=h,
    )
    assert r.status_code == 204
    login(client, "dave", "newpassword")
