# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Must be called before any os.environ.get()


class Config:
    """
    Base config. All environments inherit these.
    Use os.environ.get('VAR') or 'fallback' so:
      - In production: reads from real env vars (set by your server)
      - In development: reads from .env file
      - Fallback: safe default if neither is set
    """
    # --- Core Flask ---
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-only-insecure-key'
    # SECRET_KEY signs cookies and session data. Must be long + random in prod.
    # --- SQLAlchemy ---
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -----------render---------
    # REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
      
    # Always False — the event system wastes memory and you don't need it
    WTF_CSRF_ENABLED = True   # default True, explicit is clearer
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # --- Flask-Mail ---
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    # int() is critical — os.environ always returns strings, not ints
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    # == 'True' converts the string 'True' to a real Python boolean True
    MAIL_USE_SSL = False   # TLS and SSL are mutually exclusive — never both True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    # In testing, suppress all outgoing emails so nothing is sent for real
    MAIL_SUPPRESS_SEND = False   # overridden to True in TestingConfig

    # --- Session security ---
    SESSION_COOKIE_HTTPONLY = True   # JS can't read the session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = 3600  # session expires after 1 hour (seconds)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DEV_DATABASE_URL') or 'sqlite:///dev.db'
    )
    SQLALCHEMY_ECHO = True   # prints every SQL query — great for learning


class ProductionConfig(Config):
    DEBUG = False   # NEVER True in production
    SESSION_COOKIE_SECURE = True   # only send cookie over HTTPS
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Render gives postgres:// but SQLAlchemy needs postgresql://
    _db_url = os.environ.get('DATABASE_URL', '')
    SQLALCHEMY_DATABASE_URI = _db_url.replace(
        'postgres://', 'postgresql://', 1
    ) if _db_url else None


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-RAM, wiped after each test
    WTF_CSRF_ENABLED = False   # disable CSRF so test forms submit without tokens
    MAIL_SUPPRESS_SEND = True  # don't actually send emails during tests


# Lookup dict — used in create_app()
config_map = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}