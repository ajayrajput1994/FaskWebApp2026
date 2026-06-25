from app.model import User


class TestUserModel:
    """Tests for the User model — creation, password hashing, roles."""

    def test_create_user(self, db):
        """User can be created and saved to the DB."""
        user = User(username='newuser', email='new@example.com')
        user.set_password('secret123')
        db.session.add(user)
        db.session.commit()
        fetched = User.query.filter_by(email='new@example.com').first()
        assert fetched is not None
        assert fetched.username == 'newuser'

    def test_password_is_hashed(self, db):
        """Password is never stored as plain text."""
        user = User(username='hashtest', email='hash@example.com')
        user.set_password('mypassword')
        db.session.add(user)
        db.session.commit()
        assert user.password != 'mypassword'
        assert len(user.password) > 20   # bcrypt hash is always long

    def test_check_password_correct(self, db):
        """check_password returns True for the correct password."""
        user = User(username='pwcheck', email='pw@example.com')
        user.set_password('correcthorse')
        assert user.check_password('correcthorse') is True

    def test_check_password_wrong(self, db):
        """check_password returns False for the wrong password."""
        user = User(username='pwwrong', email='wrong@example.com')
        user.set_password('correcthorse')
        assert user.check_password('wrongpassword') is False

    def test_default_role_is_viewer(self, db):
        """New users default to viewer role."""
        user = User(username='viewer', email='viewer@example.com')
        user.set_password('pass1234')
        db.session.add(user)
        db.session.commit()
        assert user.role == 'viewer'

    def test_has_role_single(self, db, regular_user):
        """has_role returns True when user has that role."""
        assert regular_user.has_role('viewer') is True

    def test_has_role_multiple(self, db, admin_user):
        """has_role returns True if user matches any of the given roles."""
        assert admin_user.has_role('admin', 'editor') is True

    def test_has_role_false(self, db, regular_user):
        """has_role returns False when user does not have that role."""
        assert regular_user.has_role('admin') is False

    def test_count_by_role(self, db, regular_user, admin_user):
        """count_by_role returns correct counts."""
        assert User.count_by_role('viewer') == 1
        assert User.count_by_role('admin')  == 1
        assert User.count_by_role('editor') == 0

    def test_email_unique_constraint(self, db, regular_user):
        """Cannot create two users with the same email."""
        from sqlalchemy.exc import IntegrityError
        import pytest
        duplicate = User(username='other', email='test@example.com')
        duplicate.set_password('pass1234')
        db.session.add(duplicate)
        with pytest.raises(IntegrityError):
            db.session.commit()
