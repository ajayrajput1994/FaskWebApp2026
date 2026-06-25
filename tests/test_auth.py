class TestRegister:
    """POST /auth/register"""

    def test_register_page_loads(self, client):
        """GET returns 200 with the form."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Create' in response.data

    def test_register_success(self, client, db):
        """Valid data creates a user and redirects to login."""
        response = client.post('/auth/register', data={
            'username': 'brandnew',
            'email':    'brandnew@example.com',
            'password': 'Password123!',
            'confirm':  'Password123!',
        }, follow_redirects=True)
        assert response.status_code == 200
        # Should land on login page with success flash
        assert b'log in' in response.data.lower() \
            or b'Account created' in response.data

    def test_register_duplicate_email(self, client, db, regular_user):
        """Duplicate email shows validation error."""
        response = client.post('/auth/register', data={
            'username': 'someone',
            'email':    'test@example.com',   # already exists
            'password': 'Password123!',
            'confirm':  'Password123!',
        }, follow_redirects=True)
        assert b'already registered' in response.data.lower()

    def test_register_duplicate_username(self, client, db, regular_user):
        """Duplicate username shows validation error."""
        response = client.post('/auth/register', data={
            'username': 'testuser',            # already exists
            'email':    'unique@example.com',
            'password': 'Password123!',
            'confirm':  'Password123!',
        }, follow_redirects=True)
        assert b'already taken' in response.data.lower()

    def test_register_password_too_short(self, client, db):
        """Password under 8 chars fails validation."""
        response = client.post('/auth/register', data={
            'username': 'shortpw',
            'email':    'short@example.com',
            'password': '123',
            'confirm':  '123',
        })
        assert b'8 character' in response.data.lower()

    def test_register_passwords_mismatch(self, client, db):
        """Mismatched passwords fail validation."""
        response = client.post('/auth/register', data={
            'username': 'mismatch',
            'email':    'mismatch@example.com',
            'password': 'Password123!',
            'confirm':  'DifferentPass!',
        })
        assert b'do not match' in response.data.lower()

    def test_register_empty_fields(self, client, db):
        """Empty submission shows required field errors."""
        response = client.post('/auth/register', data={})
        assert b'required' in response.data.lower()

    def test_logged_in_user_redirected(self, logged_in_client):
        """Authenticated user visiting register is redirected."""
        response = logged_in_client.get('/auth/register',
                                        follow_redirects=False)
        assert response.status_code == 302


class TestLogin:
    """POST /auth/login"""

    def test_login_page_loads(self, client):
        """GET returns 200."""
        response = client.get('/auth/login')
        assert response.status_code == 200

    def test_login_success(self, client, db, regular_user):
        """Correct credentials redirect to dashboard."""
        response = client.post('/auth/login', data={
            'email':    'test@example.com',
            'password': 'Password123!',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'dashboard' in response.data.lower() \
            or b'Welcome' in response.data

    def test_login_wrong_password(self, client, db, regular_user):
        """Wrong password shows error and stays on login page."""
        response = client.post('/auth/login', data={
            'email':    'test@example.com',
            'password': 'wrongpassword',
        }, follow_redirects=True)
        assert b'invalid' in response.data.lower()

    def test_login_nonexistent_email(self, client, db):
        """Non-existent email shows same error as wrong password."""
        response = client.post('/auth/login', data={
            'email':    'nobody@example.com',
            'password': 'Password123!',
        }, follow_redirects=True)
        assert b'invalid' in response.data.lower()

    def test_login_invalid_email_format(self, client, db):
        """Malformed email triggers WTForms validator."""
        response = client.post('/auth/login', data={
            'email':    'notanemail',
            'password': 'Password123!',
        })
        assert b'valid email' in response.data.lower()

    def test_login_empty_submission(self, client, db):
        """Empty form shows required field errors."""
        response = client.post('/auth/login', data={})
        assert b'required' in response.data.lower()

    def test_login_next_redirect(self, client, db, regular_user):
        """After login, user is redirected to the ?next= page."""
        response = client.post(
            '/auth/login?next=/dashboard/profile',
            data={
                'email':    'test@example.com',
                'password': 'Password123!',
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert b'profile' in response.headers['Location']


class TestLogout:
    """GET /auth/logout"""

    def test_logout_redirects_to_login(self, logged_in_client):
        """Logout redirects to login page."""
        response = logged_in_client.get('/auth/logout',
                                        follow_redirects=True)
        assert response.status_code == 200
        assert b'log in' in response.data.lower()

    def test_logout_clears_session(self, logged_in_client):
        """After logout, protected routes redirect to login."""
        logged_in_client.get('/auth/logout')
        response = logged_in_client.get('/dashboard/',
                                        follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.headers['Location']

    def test_logout_requires_login(self, client):
        """Unauthenticated logout is redirected to login."""
        response = client.get('/auth/logout', follow_redirects=False)
        assert response.status_code == 302


class TestForgotPassword:
    """POST /auth/forgot-password"""

    def test_page_loads(self, client):
        """GET returns 200."""
        response = client.get('/auth/forgot-password')
        assert response.status_code == 200

    def test_valid_email_shows_same_message(self, client, db,
                                             regular_user):
        """Registered email shows neutral flash (no user enumeration)."""
        response = client.post('/auth/forgot-password', data={
            'email': 'test@example.com',
        }, follow_redirects=True)
        assert b'If that email' in response.data \
            or b'reset link' in response.data.lower()

    def test_unknown_email_shows_same_message(self, client, db):
        """Unknown email shows IDENTICAL message — no user enumeration."""
        response = client.post('/auth/forgot-password', data={
            'email': 'nobody@example.com',
        }, follow_redirects=True)
        assert b'If that email' in response.data \
            or b'reset link' in response.data.lower()

    def test_invalid_email_format_fails(self, client, db):
        """Malformed email triggers validator."""
        response = client.post('/auth/forgot-password', data={
            'email': 'notvalid',
        })
        assert b'valid email' in response.data.lower()
