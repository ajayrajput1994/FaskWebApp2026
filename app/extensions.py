# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


migrate = Migrate()
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
talisman = Talisman()

login_manager.login_view = 'auth.login'   # redirect if @login_required fails
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'
limiter = Limiter(
    key_func=get_remote_address,
    # Default limits apply to EVERY route unless overridden.
    # 200/day and 50/hour is a safe global ceiling.
    default_limits=['200 per day', '50 per hour'],
    # Storage URI is set in create_app() via init_app()
    # so it can read from app.config at the right time.
    storage_uri=None,   # overridden in create_app()
)
