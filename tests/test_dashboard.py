# tests/test_dashboard.py

def test_dashboard_requires_login(client):
    """Unauthenticated request is redirected to login."""
    response = client.get('/dashboard/', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


def test_dashboard_accessible_when_logged_in(logged_in_client):
    """Authenticated user can access the dashboard."""
    response = logged_in_client.get('/dashboard/')
    assert response.status_code == 200


def test_admin_page_forbidden_for_viewer(logged_in_client):
    """A viewer gets 403 on the admin users page."""
    response = logged_in_client.get('/dashboard/users')
    assert response.status_code == 403


def test_admin_page_accessible_for_admin(admin_client):
    """An admin can access the users management page."""
    response = admin_client.get('/dashboard/users')
    assert response.status_code == 200