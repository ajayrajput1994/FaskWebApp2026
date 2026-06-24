# app/auth/__init__.py
from flask import Blueprint

auth_bp = Blueprint(
    'auth',          # blueprint name — used in url_for('auth.login')
    __name__,        # tells Flask where this blueprint's templates/static live
    template_folder='../templates/auth'
)

# Import routes AFTER creating the blueprint to avoid circular imports
from . import routes   # noqa: E402, F401
from .utils import role_required, generate_reset_token, \
                   verify_reset_token, send_reset_email, \
                   send_welcome_email    # noqa