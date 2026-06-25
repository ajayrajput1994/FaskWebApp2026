# tests/conftest.py  ← CREATE

import pytest
from app import create_app
from app.extensions import db as _db
from app.model import User


@pytest.fixture(scope='session')
def app():
    """
    Session-scoped: one Flask app for the entire test run.
    Uses TestingConfig: in-memory SQLite, CSRF off, mail suppressed.
    The app is created once and reused across all test files.
    """
    application = create_app('testing')
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """
    Function-scoped database fixture.
    Wraps every test in a savepoint transaction that rolls back
    after the test finishes — so tests never affect each other.
    No data created in one test is visible in the next.
    """
    with app.app_context():
        connection  = _db.engine.connect()
        transaction = connection.begin()

        # Bind the session to the connection so all queries
        # in this test go through the same transaction
        _db.session.bind = connection

        yield _db

        _db.session.remove()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope='function')
def client(app):
    """
    Flask test client. Simulates HTTP requests without a real server.
    Use this for GET/POST/DELETE requests in route tests.
    """
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Flask CLI test runner — for testing flask CLI commands."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def regular_user(db):
    """
    Creates a viewer-role user.
    Use in tests that need a logged-out user object or a non-admin session.
    """
    user = User(
        username='testuser',
        email='test@example.com',
        role='viewer',
    )
    user.set_password('Password123!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def editor_user(db):
    """Creates an editor-role user."""
    user = User(
        username='editoruser',
        email='editor@example.com',
        role='editor',
    )
    user.set_password('Password123!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def admin_user(db):
    """Creates an admin-role user."""
    user = User(
        username='adminuser',
        email='admin@example.com',
        role='admin',
    )
    user.set_password('AdminPass123!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def logged_in_client(client, regular_user):
    """
    A test client already authenticated as a regular (viewer) user.
    Saves you from manually posting to /auth/login in every test.
    """
    client.post('/auth/login', data={
        'email':    'test@example.com',
        'password': 'Password123!',
    }, follow_redirects=True)
    return client


@pytest.fixture(scope='function')
def admin_client(client, admin_user):
    """A test client authenticated as an admin user."""
    client.post('/auth/login', data={
        'email':    'admin@example.com',
        'password': 'AdminPass123!',
    }, follow_redirects=True)
    return client


@pytest.fixture(scope='function')
def editor_client(client, editor_user):
    """A test client authenticated as an editor user."""
    client.post('/auth/login', data={
        'email':    'editor@example.com',
        'password': 'Password123!',
    }, follow_redirects=True)
    return client
