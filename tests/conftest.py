# tests/conftest.py
import pytest
from app import create_app
from app.extensions import db as _db
from app.model import User


@pytest.fixture(scope='session')
def app():
    """
    Session-scoped: one app for the whole test run.
    Uses TestingConfig: in-memory DB, CSRF disabled.
    """
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """
    Function-scoped: each test gets a clean database.
    Uses nested transactions that roll back after each test —
    so tests never affect each other.
    """
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        _db.session.bind = connection
        yield _db
        _db.session.remove()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(app):
    """The Flask test client — simulates HTTP requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """The Flask CLI test runner — for testing flask commands."""
    return app.test_cli_runner()


@pytest.fixture
def regular_user(db):
    """Creates a standard viewer user for tests."""
    user = User(username='testuser', email='test@example.com', role='viewer')
    user.set_password('Password123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_user(db):
    """Creates an admin user for tests."""
    user = User(username='adminuser', email='admin@example.com', role='admin')
    user.set_password('AdminPass123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def logged_in_client(client, regular_user):
    """Returns a test client that is already logged in as a regular user."""
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'Password123',
    })
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Returns a test client already logged in as admin."""
    client.post('/auth/login', data={
        'email': 'admin@example.com',
        'password': 'AdminPass123',
    })
    return client