# tests/test_api.py
import json


def test_status_endpoint_is_public(client):
    """The /api/v1/status endpoint works without login."""
    response = client.get('/api/v1/status')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'


def test_me_requires_login(client):
    """The /api/v1/me endpoint returns 401 when not logged in."""
    response = client.get('/api/v1/me')
    # Flask-Login redirects unauthenticated requests to login
    assert response.status_code in (401, 302)


def test_me_returns_user_data(logged_in_client):
    """Logged-in user gets their own data from /api/v1/me."""
    response = logged_in_client.get('/api/v1/me')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['email'] == 'test@example.com'
    assert data['role'] == 'viewer'


def test_users_list_forbidden_for_viewer(logged_in_client):
    """Non-admin gets 403 on the /api/v1/users list."""
    response = logged_in_client.get('/api/v1/users')
    assert response.status_code == 403


def test_users_list_accessible_for_admin(admin_client, db, regular_user):
    """Admin gets a list of all users."""
    response = admin_client.get('/api/v1/users')
    assert response.status_code == 200
    data = json.loads(response.data)
    emails = [u['email'] for u in data]
    assert 'test@example.com' in emails