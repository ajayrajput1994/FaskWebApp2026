# tests/test_auth.py

def test_register_success(client, db):
    """A new user can register with valid data."""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email':    'new@example.com',
        'password': 'Password123',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'log in' in response.data.lower()


def test_register_duplicate_email(client, db, regular_user):
    """Registration with an existing email shows an error."""
    response = client.post('/auth/register', data={
        'username': 'anotheruser',
        'email':    'test@example.com',  # already exists
        'password': 'Password123',
    }, follow_redirects=True)
    assert b'already registered' in response.data.lower()


def test_login_success(client, db, regular_user):
    """Correct credentials redirect to dashboard."""
    response = client.post('/auth/login', data={
        'email':    'test@example.com',
        'password': 'Password123',
    }, follow_redirects=True)
    assert response.status_code == 200
    # Should land on dashboard
    assert b'dashboard' in response.data.lower()


def test_login_wrong_password(client, db, regular_user):
    """Wrong password stays on login with error."""
    response = client.post('/auth/login', data={
        'email':    'test@example.com',
        'password': 'wrongpassword',
    }, follow_redirects=True)
    assert b'invalid' in response.data.lower()


def test_logout(logged_in_client):
    """Logged-in user can log out and is redirected to login."""
    response = logged_in_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    # After logout, visiting dashboard should redirect to login
    response = logged_in_client.get('/dashboard/', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']