import json


class TestStatusEndpoint:
    """GET /api/v1/status — public"""

    def test_status_is_public(self, client):
        """No authentication needed."""
        r = client.get('/api/v1/status')
        assert r.status_code == 200

    def test_status_returns_json(self, client):
        """Response is valid JSON."""
        r = client.get('/api/v1/status')
        data = json.loads(r.data)
        assert data['status'] == 'ok'

    def test_status_has_version(self, client):
        """Response includes a version field."""
        r = client.get('/api/v1/status')
        data = json.loads(r.data)
        assert 'version' in data


class TestMeEndpoint:
    """GET /api/v1/me — requires login"""

    def test_me_requires_auth(self, client):
        """Unauthenticated request is redirected or returns 401."""
        r = client.get('/api/v1/me')
        assert r.status_code in (302, 401)

    def test_me_returns_own_data(self, logged_in_client, regular_user):
        """Logged-in user gets their own profile data."""
        r = logged_in_client.get('/api/v1/me')
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data['email']    == 'test@example.com'
        assert data['username'] == 'testuser'
        assert data['role']     == 'viewer'

    def test_me_does_not_expose_password(self, logged_in_client):
        """Password hash must never appear in the response."""
        r = logged_in_client.get('/api/v1/me')
        data = json.loads(r.data)
        assert 'password' not in data


class TestUsersListEndpoint:
    """GET /api/v1/users — admin only"""

    def test_users_list_blocked_for_viewer(self, logged_in_client):
        """Viewer gets 403."""
        r = logged_in_client.get('/api/v1/users')
        assert r.status_code == 403

    def test_users_list_blocked_for_unauthenticated(self, client):
        """Unauthenticated request is redirected or 401."""
        r = client.get('/api/v1/users')
        assert r.status_code in (302, 401)

    def test_users_list_accessible_to_admin(self, admin_client):
        """Admin gets a list of users."""
        r = admin_client.get('/api/v1/users')
        assert r.status_code == 200
        data = json.loads(r.data)
        assert isinstance(data, list)

    def test_users_list_contains_created_users(self, admin_client,
                                                db, regular_user):
        """Created users appear in the list."""
        r = admin_client.get('/api/v1/users')
        data = json.loads(r.data)
        emails = [u['email'] for u in data]
        assert 'test@example.com' in emails

    def test_users_list_no_passwords(self, admin_client, db,
                                      regular_user):
        """Password hashes must never appear in the list."""
        r = admin_client.get('/api/v1/users')
        data = json.loads(r.data)
        for user in data:
            assert 'password' not in user
