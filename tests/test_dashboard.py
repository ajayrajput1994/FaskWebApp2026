from app.model import User


class TestDashboardAccess:
    """Route access by authentication and role."""

    def test_index_requires_login(self, client):
        """Unauthenticated → redirect to login."""
        r = client.get('/dashboard/', follow_redirects=False)
        assert r.status_code == 302
        assert 'login' in r.headers['Location']

    def test_index_accessible_when_logged_in(self, logged_in_client):
        """Any authenticated user can reach the dashboard."""
        r = logged_in_client.get('/dashboard/')
        assert r.status_code == 200

    def test_profile_requires_login(self, client):
        """Profile page blocks unauthenticated users."""
        r = client.get('/dashboard/profile', follow_redirects=False)
        assert r.status_code == 302

    def test_profile_accessible_to_viewer(self, logged_in_client):
        """Viewer can see their own profile."""
        r = logged_in_client.get('/dashboard/profile')
        assert r.status_code == 200

    def test_editor_page_blocks_viewer(self, logged_in_client):
        """Viewer gets 403 on editor-only page."""
        r = logged_in_client.get('/dashboard/editor')
        assert r.status_code == 403

    def test_editor_page_allows_editor(self, editor_client):
        """Editor can access editor page."""
        r = editor_client.get('/dashboard/editor')
        assert r.status_code == 200

    def test_editor_page_allows_admin(self, admin_client):
        """Admin can also access editor page."""
        r = admin_client.get('/dashboard/editor')
        assert r.status_code == 200

    def test_admin_panel_blocks_viewer(self, logged_in_client):
        """Viewer gets 403 on admin panel."""
        r = logged_in_client.get('/dashboard/admin')
        assert r.status_code == 403

    def test_admin_panel_blocks_editor(self, editor_client):
        """Editor gets 403 on admin panel."""
        r = editor_client.get('/dashboard/admin')
        assert r.status_code == 403

    def test_admin_panel_allows_admin(self, admin_client):
        """Admin can access admin panel."""
        r = admin_client.get('/dashboard/admin')
        assert r.status_code == 200


class TestAdminActions:
    """POST actions on user management — admin only."""

    def test_change_role_success(self, admin_client, db, regular_user):
        """Admin can change another user's role."""
        r = admin_client.post(
            f'/dashboard/admin/change-role/{regular_user.id}',
            data={'role': 'editor', 'csrf_token': 'test'},
            follow_redirects=True,
        )
        assert r.status_code == 200
        updated = User.query.get(regular_user.id)
        assert updated.role == 'editor'

    def test_change_role_invalid_role(self, admin_client, db,
                                       regular_user):
        """Invalid role name is rejected."""
        r = admin_client.post(
            f'/dashboard/admin/change-role/{regular_user.id}',
            data={'role': 'superuser', 'csrf_token': 'test'},
            follow_redirects=True,
        )
        # Role should be unchanged
        unchanged = User.query.get(regular_user.id)
        assert unchanged.role == 'viewer'

    def test_cannot_change_own_role(self, admin_client, db,
                                     admin_user):
        """Admin cannot change their own role."""
        r = admin_client.post(
            f'/dashboard/admin/change-role/{admin_user.id}',
            data={'role': 'viewer', 'csrf_token': 'test'},
            follow_redirects=True,
        )
        assert b'cannot change your own' in r.data.lower()
        # Role must be unchanged
        still_admin = User.query.get(admin_user.id)
        assert still_admin.role == 'admin'

    def test_change_role_blocked_for_viewer(self, logged_in_client,
                                             db, admin_user):
        """Viewer gets 403 when trying to change roles."""
        r = logged_in_client.post(
            f'/dashboard/admin/change-role/{admin_user.id}',
            data={'role': 'viewer', 'csrf_token': 'test'},
        )
        assert r.status_code == 403

    def test_delete_user_success(self, admin_client, db, regular_user):
        """Admin can delete another user."""
        user_id = regular_user.id
        r = admin_client.post(
            f'/dashboard/admin/delete/{user_id}',
            data={'csrf_token': 'test'},
            follow_redirects=True,
        )
        assert r.status_code == 200
        assert User.query.get(user_id) is None

    def test_cannot_delete_self(self, admin_client, db, admin_user):
        """Admin cannot delete their own account via this route."""
        r = admin_client.post(
            f'/dashboard/admin/delete/{admin_user.id}',
            data={'csrf_token': 'test'},
            follow_redirects=True,
        )
        assert b'cannot delete your own' in r.data.lower()
        assert User.query.get(admin_user.id) is not None

    def test_delete_nonexistent_user(self, admin_client, db):
        """Deleting a non-existent user returns 404."""
        r = admin_client.post(
            '/dashboard/admin/delete/99999',
            data={'csrf_token': 'test'},
        )
        assert r.status_code == 404

    def test_admin_search(self, admin_client, db, regular_user):
        """Admin search filters by username."""
        r = admin_client.get('/dashboard/admin?q=testuser')
        assert r.status_code == 200
        assert b'testuser' in r.data

    def test_admin_search_no_results(self, admin_client, db):
        """Search with no match shows empty state."""
        r = admin_client.get('/dashboard/admin?q=zzznobody')
        assert r.status_code == 200
        assert b'No users found' in r.data
